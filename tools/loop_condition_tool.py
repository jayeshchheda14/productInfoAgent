from google.adk.tools import ToolContext
from .. import config

def check_gatekeeper_condition(tool_context: ToolContext) -> str:
    """Check if the gatekeeper conditions are met to stop the loop"""
    
    # Get the scoring results from the callback context
    scoring_result = tool_context.callback_context.state.get("scoring_result", {})
    
    # Check if gatekeeper passed
    gatekeeper_passed = scoring_result.get("gatekeeper_passed", False)
    score = scoring_result.get("score", 0)
    
    if gatekeeper_passed:
        # Stop the loop - gatekeeper approved
        tool_context.actions.escalate = True
        return f"✅ Gatekeeper APPROVED with score {score}. Proceeding to marketing generation."
    else:
        # Check if we've reached max iterations
        current_iteration = tool_context.callback_context.state.get("iteration_count", 0) + 1
        tool_context.callback_context.state["iteration_count"] = current_iteration
        
        if current_iteration >= config.MAX_ITERATIONS:
            # Stop the loop - max iterations reached
            tool_context.actions.escalate = True
            rejection_reason = scoring_result.get("rejection_reason", "Unknown reason")
            return f"🚫 Gatekeeper REJECTED after {current_iteration} iterations. Reason: {rejection_reason}"
        else:
            # Continue the loop
            return f"⚠️ Gatekeeper check failed (iteration {current_iteration}/{config.MAX_ITERATIONS}). Retrying..."