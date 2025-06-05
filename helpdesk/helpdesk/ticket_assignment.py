import frappe
from frappe.utils import now_datetime
from datetime import datetime

def assign_unassigned_tickets_round_robin():
    # 1. Get all UNASSIGNED open tickets (where agent field is empty)
    unassigned_tickets = frappe.get_all("HD Ticket",
        filters={
            "status": "Open",
            "agent": ["in", ["", None]]  # Explicitly check for empty or NULL
        },
        fields=["name", "creation"],
        order_by="creation asc"  # Oldest tickets first
    )

    if not unassigned_tickets:
        frappe.log("No unassigned tickets found")
        return

    # 2. Get online agents sorted by last assignment (oldest first)
    online_agents = frappe.get_all("HD Agent",
        filters={
            "custom_current_status": "Online",
            "enabled": 1  # Only active agents
        },
        fields=["name", "last_assignment"],
        order_by="last_assignment asc"  # Agent with oldest assignment first
    )

    if not online_agents:
        frappe.log("No online agents available")
        return

    # 3. Round-robin assignment
    assignments = 0
    agent_index = 0

    for ticket in unassigned_tickets:
        current_agent = online_agents[agent_index]

        try:
            # Assign ticket
            frappe.db.set_value("HD Ticket", ticket.name, {
                "agent": current_agent.name,
                "assignment_date": now_datetime()
            })

            # Update agent's last assignment time
            frappe.db.set_value("HD Agent", current_agent.name, "last_assignment", now_datetime())

            assignments += 1
            frappe.db.commit()

            # Move to next agent
            agent_index = (agent_index + 1) % len(online_agents)

        except Exception as e:
            frappe.log_error(f"Failed to assign ticket {ticket.name}: {str(e)}")
            frappe.db.rollback()

    frappe.msgprint(f"Assigned {assignments} unassigned tickets to {len(online_agents)} online agents")

# For manual testing via bench console
if __name__ == "__main__":
    assign_unassigned_tickets_round_robin()