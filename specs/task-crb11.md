# CRB-11 - Client status lifecycle transitions
Add a transition_to(new_status) method to the existing Client class in src/fractional_crm/client.py.
Allowed transitions: prospect->active, active->paused, paused->active, active->closed, paused->closed.
Any other transition (including to an unknown status value) raises ValueError and leaves self.status unchanged.
On an allowed transition, set self.status to new_status. Do NOT change any existing Client behavior or break existing tests. Do not modify tests.
