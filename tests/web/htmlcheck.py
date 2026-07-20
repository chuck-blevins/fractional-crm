"""Structural HTML conformance checks for the server-rendered pages (CRB-32 follow-up).

WHY THIS EXISTS: the CRB-32 timeline fragment shipped a ``<p>`` nested directly inside an
``<ol>`` — invalid HTML — and every one of the six story tests passed, because they only
assert that certain strings appear. Behavioural assertions pin *behaviour*; nothing pinned
*markup validity*, so the defect was caught by a human reading the output.

Note that an HTML5 *parser* would not have caught it either: the HTML5 parsing algorithm is
deliberately permissive and ``<ol><p>x</p></ol>`` parses without error. What it violates is the
element's *content model*, which is a conformance concern. Real conformance checking means the
Nu validator (Java), which is not installed on the build box and is a heavy dependency for one
class of defect. This module implements the subset that matters for this codebase, using only
the standard library:

* element nesting is balanced (with HTML5 implied-end-tag handling, so omitting ``</li>`` is
  not reported as an error);
* content models for the list/table/select containers, where "only these children are legal"
  is a hard rule — this is the CRB-32 defect;
* ``id`` uniqueness;
* every ``label[for]`` resolves to a real element;
* every form control is labelled (CRB-29 accessibility baseline);
* exactly one ``<h1>`` per full page.

Deliberately NOT a general validator. It reports what it can prove, and stays quiet elsewhere.
"""
from html.parser import HTMLParser

#: Elements that never have children or an end tag.
VOID = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
})

#: Containers whose direct children are constrained by the HTML5 content model.
#: Text (other than whitespace) is illegal in all of them.
ALLOWED_CHILDREN = {
    "ol": {"li", "script", "template"},
    "ul": {"li", "script", "template"},
    "menu": {"li", "script", "template"},
    "dl": {"dt", "dd", "div", "script", "template"},
    "table": {"caption", "colgroup", "thead", "tbody", "tfoot", "tr", "script", "template"},
    "thead": {"tr", "script", "template"},
    "tbody": {"tr", "script", "template"},
    "tfoot": {"tr", "script", "template"},
    "tr": {"td", "th", "script", "template"},
    "select": {"option", "optgroup", "script", "template"},
    "optgroup": {"option", "script", "template"},
}

#: start tag -> open elements it implicitly closes (HTML5 optional end tags).
_IMPLIED_END = {
    "li": {"li"},
    "dt": {"dt", "dd"},
    "dd": {"dt", "dd"},
    "option": {"option"},
    "optgroup": {"option", "optgroup"},
    "tr": {"td", "th", "tr"},
    "td": {"td", "th"},
    "th": {"td", "th"},
    "thead": {"td", "th", "tr"},
    "tbody": {"td", "th", "tr", "thead"},
    "tfoot": {"td", "th", "tr", "tbody"},
}

#: A <p> is implicitly closed by any of these block-level start tags.
_CLOSES_P = frozenset({
    "address", "article", "aside", "blockquote", "details", "div", "dl", "fieldset",
    "figcaption", "figure", "footer", "form", "h1", "h2", "h3", "h4", "h5", "h6",
    "header", "hr", "main", "nav", "ol", "p", "pre", "section", "table", "ul",
})

#: Elements whose end tag may be omitted when the parent closes — ``<ul><li>a<li>b</ul>`` is
#: conformant HTML5, so leaving these open at a parent's end tag is not an error.
_OPTIONAL_END = frozenset({
    "li", "dt", "dd", "p", "option", "optgroup", "td", "th", "tr",
    "thead", "tbody", "tfoot", "caption", "colgroup",
})

#: input types that are self-describing and need no associated <label>.
_UNLABELLED_INPUT_TYPES = frozenset({"hidden", "submit", "reset", "button", "image"})


class _Node:
    """One element in the parsed tree. ``children`` holds child _Node objects and text strings."""

    def __init__(self, tag, attrs, line, parent=None):
        self.tag = tag
        self.attrs = dict(attrs)
        self.line = line
        self.parent = parent
        self.children = []

    def walk(self):
        """Yield this node and every descendant element, depth first."""
        yield self
        for child in self.children:
            if isinstance(child, _Node):
                yield from child.walk()


class _TreeBuilder(HTMLParser):
    """Build a _Node tree, recording structural errors as it goes."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = _Node("#document", {}, 0)
        self.stack = [self.root]
        self.errors = []

    def _close_implied(self, tag):
        """Pop open elements that this start tag implicitly closes."""
        implied = _IMPLIED_END.get(tag, set())
        if tag in _CLOSES_P:
            implied = implied | {"p"}
        while len(self.stack) > 1 and self.stack[-1].tag in implied:
            self.stack.pop()

    def handle_starttag(self, tag, attrs):
        self._close_implied(tag)
        node = _Node(tag, attrs, self.getpos()[0], self.stack[-1])
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        # <foo /> — self-closing, never pushed.
        node = _Node(tag, attrs, self.getpos()[0], self.stack[-1])
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not any(n.tag == tag for n in self.stack[1:]):
            self.errors.append(f"line {self.getpos()[0]}: stray </{tag}> with no matching open tag")
            return
        # Close everything up to and including the matching open element. Anything skipped
        # was left unclosed.
        while len(self.stack) > 1:
            node = self.stack.pop()
            if node.tag == tag:
                break
            if node.tag in _OPTIONAL_END:
                continue  # e.g. <ul><li>a<li>b</ul> — omitting </li> is conformant.
            self.errors.append(
                f"line {node.line}: <{node.tag}> is not closed before </{tag}> on line {self.getpos()[0]}"
            )

    def handle_data(self, data):
        if data.strip():
            self.stack[-1].children.append(data)

    def close(self):
        super().close()
        for node in self.stack[1:]:
            if node.tag in _OPTIONAL_END:
                continue
            self.errors.append(f"line {node.line}: <{node.tag}> is never closed")


def _check_content_models(root, errors):
    """Flag children that the HTML5 content model forbids (the CRB-32 defect)."""
    for node in root.walk():
        allowed = ALLOWED_CHILDREN.get(node.tag)
        if allowed is None:
            continue
        for child in node.children:
            if isinstance(child, str):
                errors.append(
                    f"line {node.line}: text is not allowed as a direct child of <{node.tag}> "
                    f"(found {child.strip()[:40]!r})"
                )
            elif child.tag not in allowed:
                errors.append(
                    f"line {child.line}: <{child.tag}> is not allowed as a direct child of "
                    f"<{node.tag}> (allowed: {', '.join(sorted(allowed))})"
                )


def _check_ids_and_labels(root, errors):
    """Flag duplicate ids, dangling label[for], and unlabelled form controls."""
    ids = {}
    for node in root.walk():
        node_id = node.attrs.get("id")
        if node_id is None:
            continue
        if node_id in ids:
            errors.append(
                f"line {node.line}: duplicate id={node_id!r} (first used on line {ids[node_id]})"
            )
        else:
            ids[node_id] = node.line

    labelled_ids = set()
    for node in root.walk():
        if node.tag != "label":
            continue
        target = node.attrs.get("for")
        if target is None:
            continue
        labelled_ids.add(target)
        if target not in ids:
            errors.append(f"line {node.line}: <label for={target!r}> does not match any element id")

    for node in root.walk():
        if node.tag not in {"input", "select", "textarea"}:
            continue
        if node.tag == "input" and node.attrs.get("type", "text") in _UNLABELLED_INPUT_TYPES:
            continue
        if "aria-label" in node.attrs or "aria-labelledby" in node.attrs:
            continue
        if node.attrs.get("id") in labelled_ids:
            continue
        ancestor = node.parent
        while ancestor is not None:
            if ancestor.tag == "label":
                break
            ancestor = ancestor.parent
        else:
            errors.append(
                f"line {node.line}: <{node.tag}"
                f"{' name=' + repr(node.attrs['name']) if 'name' in node.attrs else ''}> "
                "has no associated <label> and no aria-label"
            )


def _check_headings(root, errors):
    """Flag a full page that does not have exactly one <h1>."""
    h1s = [n for n in root.walk() if n.tag == "h1"]
    if len(h1s) != 1:
        where = ", ".join(f"line {n.line}" for n in h1s) or "none found"
        errors.append(f"expected exactly one <h1> on a page, found {len(h1s)} ({where})")


def validate(html, *, fragment=False):
    """Return a list of conformance problems in ``html``; empty means it looks well formed.

    Set ``fragment=True`` for HTMX partials, which are not whole documents and so are exempt
    from the single-``<h1>`` rule.
    """
    builder = _TreeBuilder()
    builder.feed(html)
    builder.close()
    errors = list(builder.errors)
    _check_content_models(builder.root, errors)
    _check_ids_and_labels(builder.root, errors)
    if not fragment:
        _check_headings(builder.root, errors)
    return errors


def assert_valid_html(html, *, context="", fragment=False):
    """Raise AssertionError listing every conformance problem found in ``html``."""
    errors = validate(html, fragment=fragment)
    if errors:
        where = f" for {context}" if context else ""
        listed = "\n  - ".join(errors)
        raise AssertionError(f"invalid HTML{where}:\n  - {listed}")
