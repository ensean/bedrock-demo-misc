from flask import Flask, render_template, request, jsonify
from strands import Agent
from strands.agent.conversation_manager import (
    NullConversationManager,
    SlidingWindowConversationManager,
    SummarizingConversationManager
)
from strands.models import BedrockModel
import os
from datetime import datetime

app = Flask(__name__)

# Store results for comparison
results_store = []

def create_agent(manager_type, use_cache=True):
    """Create an agent with specified conversation manager and cache settings."""
    
    # Create conversation manager based on type
    if manager_type == "null":
        manager = NullConversationManager()
    elif manager_type == "sliding":
        manager = SlidingWindowConversationManager(window_size=2)
    elif manager_type == "summarizing":
        manager = SummarizingConversationManager(
            summary_ratio=0.3,
            preserve_recent_messages=2
        )
    else:
        raise ValueError(f"Unknown manager type: {manager_type}")
    
    bedrock_model = BedrockModel(
        model_id="global.anthropic.claude-sonnet-4-5-20250929-v1:0",
        temperature=0.3,
    )
    
    # Create agent with Bedrock configuration
    agent = Agent(
        name=f"TokenOptimizer-{manager_type}",
        model=bedrock_model,
        conversation_manager=manager
    )
    
    return agent

def get_token_stats_from_trace(trace):
    """Extract token usage statistics from trace result."""
    stats = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_creation_tokens": 0,
        "cache_read_tokens": 0,
        "total_tokens": 0
    }
    
    # Get metrics from trace
    if hasattr(trace, 'metrics'):
        metrics_summary = trace.metrics.get_summary()
        accumulated_usage = metrics_summary.get("accumulated_usage", {})
        
        stats["input_tokens"] = accumulated_usage.get("inputTokens", 0)
        stats["output_tokens"] = accumulated_usage.get("outputTokens", 0)
        stats["total_tokens"] = accumulated_usage.get("totalTokens", 0)
        
        # Check for cache tokens in the usage details
        if "cacheCreationInputTokens" in accumulated_usage:
            stats["cache_creation_tokens"] = accumulated_usage.get("cacheCreationInputTokens", 0)
        if "cacheReadInputTokens" in accumulated_usage:
            stats["cache_read_tokens"] = accumulated_usage.get("cacheReadInputTokens", 0)
    
    return stats

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test', methods=['POST'])
def test_configuration():
    """Test a specific configuration and return token usage."""
    data = request.json
    manager_type = data.get('manager_type', 'null')
    use_cache = data.get('use_cache', True)
    messages = data.get('messages', [])
    
    if not messages:
        return jsonify({"error": "No messages provided"}), 400
    
    try:
        # Create agent
        agent = create_agent(manager_type, use_cache)
        
        # Process messages and accumulate stats
        responses = []
        conversation = []
        accumulated_stats = {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_creation_tokens": 0,
            "cache_read_tokens": 0,
            "total_tokens": 0
        }
        
        for msg in messages:
            # Add user message to conversation
            conversation.append({
                "role": "user",
                "content": msg
            })
            
            trace = agent(msg)
            
            # Extract text from trace object
            response_text = ""
            if hasattr(trace, 'text'):
                response_text = trace.text
            elif hasattr(trace, 'output_text'):
                response_text = trace.output_text
            else:
                response_text = str(trace)
            
            responses.append(response_text)
            
            # Get token statistics for this specific response
            trace_stats = get_token_stats_from_trace(trace)
            
            # Calculate cost for this response
            msg_input_cost = trace_stats["input_tokens"] * 0.003 / 1000
            msg_output_cost = trace_stats["output_tokens"] * 0.015 / 1000
            msg_cache_write_cost = trace_stats["cache_creation_tokens"] * 0.00375 / 1000
            msg_cache_read_cost = trace_stats["cache_read_tokens"] * 0.0003 / 1000
            msg_total_cost = msg_input_cost + msg_output_cost + msg_cache_write_cost + msg_cache_read_cost
            
            # Add assistant response with token info
            conversation.append({
                "role": "assistant",
                "content": response_text,
                "tokens": trace_stats,
                "cost": round(msg_total_cost, 6)
            })
            
            # Accumulate token statistics
            for key in accumulated_stats:
                accumulated_stats[key] += trace_stats[key]
        
        stats = accumulated_stats
        
        # Calculate estimated cost (Claude 3.5 Sonnet pricing)
        input_cost = stats["input_tokens"] * 0.003 / 1000
        output_cost = stats["output_tokens"] * 0.015 / 1000
        cache_write_cost = stats["cache_creation_tokens"] * 0.00375 / 1000
        cache_read_cost = stats["cache_read_tokens"] * 0.0003 / 1000
        total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost
        
        result = {
            "manager_type": manager_type,
            "use_cache": use_cache,
            "timestamp": datetime.now().isoformat(),
            "stats": stats,
            "cost": {
                "input": round(input_cost, 6),
                "output": round(output_cost, 6),
                "cache_write": round(cache_write_cost, 6),
                "cache_read": round(cache_read_cost, 6),
                "total": round(total_cost, 6)
            },
            "responses": responses,
            "conversation": conversation,
            "message_count": len(messages)
        }
        
        # Store result
        results_store.append(result)
        
        return jsonify(result)
    
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/compare', methods=['POST'])
def compare_configurations():
    """Compare multiple configurations side by side."""
    data = request.json
    messages = data.get('messages', [])
    
    if not messages:
        return jsonify({"error": "No messages provided"}), 400
    
    configurations = [
        {"manager_type": "null", "use_cache": False},
        {"manager_type": "null", "use_cache": True},
        {"manager_type": "sliding", "use_cache": False},
        {"manager_type": "sliding", "use_cache": True},
        {"manager_type": "summarizing", "use_cache": False},
        {"manager_type": "summarizing", "use_cache": True},
    ]
    
    results = []
    
    for config in configurations:
        try:
            agent = create_agent(config["manager_type"], config["use_cache"])
            
            # Process messages and accumulate stats
            conversation = []
            accumulated_stats = {
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_creation_tokens": 0,
                "cache_read_tokens": 0,
                "total_tokens": 0
            }
            
            for msg in messages:
                # Add user message
                conversation.append({
                    "role": "user",
                    "content": msg
                })
                
                trace = agent(msg)
                
                # Extract response text
                response_text = ""
                if hasattr(trace, 'text'):
                    response_text = trace.text
                elif hasattr(trace, 'output_text'):
                    response_text = trace.output_text
                else:
                    response_text = str(trace)
                
                # Get token statistics for this specific response
                trace_stats = get_token_stats_from_trace(trace)
                
                # Calculate cost for this response
                msg_input_cost = trace_stats["input_tokens"] * 0.003 / 1000
                msg_output_cost = trace_stats["output_tokens"] * 0.015 / 1000
                msg_cache_write_cost = trace_stats["cache_creation_tokens"] * 0.00375 / 1000
                msg_cache_read_cost = trace_stats["cache_read_tokens"] * 0.0003 / 1000
                msg_total_cost = msg_input_cost + msg_output_cost + msg_cache_write_cost + msg_cache_read_cost
                
                # Add assistant response with token info
                conversation.append({
                    "role": "assistant",
                    "content": response_text,
                    "tokens": trace_stats,
                    "cost": round(msg_total_cost, 6)
                })
                
                # Accumulate token statistics
                for key in accumulated_stats:
                    accumulated_stats[key] += trace_stats[key]
            
            stats = accumulated_stats
            
            # Calculate cost
            input_cost = stats["input_tokens"] * 0.003 / 1000
            output_cost = stats["output_tokens"] * 0.015 / 1000
            cache_write_cost = stats["cache_creation_tokens"] * 0.00375 / 1000
            cache_read_cost = stats["cache_read_tokens"] * 0.0003 / 1000
            total_cost = input_cost + output_cost + cache_write_cost + cache_read_cost
            
            results.append({
                "manager_type": config["manager_type"],
                "use_cache": config["use_cache"],
                "stats": stats,
                "cost": {
                    "total": round(total_cost, 6)
                },
                "conversation": conversation
            })
        
        except Exception as e:
            import traceback
            results.append({
                "manager_type": config["manager_type"],
                "use_cache": config["use_cache"],
                "error": str(e),
                "traceback": traceback.format_exc()
            })
    
    return jsonify({"results": results})

@app.route('/history')
def get_history():
    """Get test history."""
    return jsonify({"history": results_store})

if __name__ == '__main__':
    # Check for AWS credentials
    if not os.getenv('AWS_ACCESS_KEY_ID') and not os.getenv('AWS_PROFILE'):
        print("Warning: AWS credentials not configured")
        print("Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY or configure AWS_PROFILE")
    
    if not os.getenv('AWS_REGION'):
        print("Warning: AWS_REGION not set, defaulting to us-east-1")
        os.environ['AWS_REGION'] = 'us-east-1'
    
    app.run(debug=True, port=5000)
