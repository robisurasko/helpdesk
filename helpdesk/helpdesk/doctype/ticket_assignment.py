import frappe
from frappe.utils import now_datetime, get_datetime_str
from frappe.desk.form.assign_to import add as add_assignment

def assign_unassigned_tickets_round_robin():
    """Assign unassigned tickets with max 5 per agent when alone"""
    
    def log_action(message, status="INFO", details=None):
        timestamp = get_datetime_str(now_datetime())
        log_entry = f"[{timestamp}] [{status}] {message}"
        if details:
            log_entry += f"\nDetails: {str(details)}"
        print(log_entry)
        if status != "INFO":
            frappe.log_error(title="Ticket Assignment", message=log_entry)

    log_action("Starting ticket assignment process")
    
    try:
        # 1. Get unassigned tickets
        unassigned_tickets = frappe.get_all(
            "HD Ticket",
            filters={
                "status": "Open",
                "_assign": ["in", ["", None]]
            },
            fields=["name"],
            order_by="creation asc",
            ignore_permissions=True
        )

        if not unassigned_tickets:
            log_action("No unassigned tickets found")
            return {
                "status": "success",
                "message": "No unassigned tickets found",
                "assigned": 0
            }

        log_action(f"Found {len(unassigned_tickets)} unassigned tickets")

        # 2. Get online agents
        online_agents = frappe.get_all(
            "HD Agent",
            filters={
                "custom_current_status": "Online",
                "is_active": 1
            },
            fields=["name", "user"],
            order_by="custom_last_assignment asc",
            ignore_permissions=True
        )

        if not online_agents:
            log_action("No online agents available", "WARNING")
            return {
                "status": "failed",
                "message": "No online agents available",
                "assigned": 0
            }

        log_action(f"Found {len(online_agents)} online agents")

        # 3. Initialize in-memory assignment tracking
        agent_assignments = {agent['user']: 0 for agent in online_agents}
        assignments = 0
        assignment_results = []

        for ticket in unassigned_tickets:
            # Sort agents by: 1. assignment count, 2. last assignment time
            sorted_agents = sorted(
                online_agents,
                key=lambda x: (
                    agent_assignments[x['user']],
                    frappe.db.get_value("HD Agent", x['name'], "custom_last_assignment") or "2000-01-01"
                )
            )

            agent_assigned = False
            for agent in sorted_agents:
                # Skip if single agent has reached max assignments
                if len(online_agents) == 1 and agent_assignments[agent['user']] >= 5:
                    continue

                ticket_name = ticket['name']
                agent_user = agent['user']

                try:
                    agent_email = frappe.db.get_value("User", agent_user, "email")
                    if not agent_email:
                        log_action(f"Skipping agent {agent_user} - no email found", "WARNING")
                        continue

                    # Create assignment
                    add_assignment({
                        'doctype': "HD Ticket",
                        'name': ticket_name,
                        'assign_to': [agent_email],
                        'description': "Automatically assigned",
                        'notify': True
                    })

                    # Update last assignment time
                    frappe.db.set_value(
                        "HD Agent",
                        agent['name'],
                        "custom_last_assignment",
                        now_datetime(),
                        update_modified=False
                    )

                    # Update in-memory counter
                    agent_assignments[agent_user] += 1
                    assignments += 1
                    assignment_results.append({
                        "ticket": ticket_name,
                        "agent": agent_user,
                        "status": "success",
                        "timestamp": get_datetime_str(now_datetime())
                    })
                    frappe.db.commit()
                    log_action(f"Assigned {ticket_name} to {agent_user}")
                    agent_assigned = True
                    break

                except Exception as e:
                    frappe.db.rollback()
                    assignment_results.append({
                        "ticket": ticket_name,
                        "agent": agent_user,
                        "status": "failed",
                        "error": str(e)
                    })
                    log_action(f"Failed to assign {ticket_name}: {str(e)}", "ERROR")

            if not agent_assigned:
                log_action(f"No available agents for ticket {ticket['name']}", "WARNING")
                assignment_results.append({
                    "ticket": ticket['name'],
                    "status": "failed",
                    "error": "No available agents (max assignments reached)"
                })

        # 4. Return results
        result = {
            "status": "success" if assignments > 0 else "partial",
            "total_tickets": len(unassigned_tickets),
            "assigned": assignments,
            "failed": len(unassigned_tickets) - assignments,
            "assignments": assignment_results
        }

        log_action(f"Completed: {assignments} assignments made")
        return result

    except Exception as e:
        frappe.db.rollback()
        log_action(f"Process failed: {str(e)}", "CRITICAL")
        return {
            "status": "failed",
            "error": str(e)
        }