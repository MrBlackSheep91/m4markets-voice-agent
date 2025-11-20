"""
Cost Metrics and Performance Monitoring for M4Markets Voice Agent
Tracks API usage, latency, and costs in real-time
"""

import time
from typing import Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class CallMetrics:
    """Metrics for a single call"""
    call_id: str
    start_time: float = field(default_factory=time.time)

    # Token usage
    stt_seconds: float = 0.0  # Speech-to-text audio seconds
    tts_characters: int = 0  # Text-to-speech characters
    llm_input_tokens: int = 0
    llm_output_tokens: int = 0

    # Tool usage
    tool_calls: int = 0
    tool_call_times: list = field(default_factory=list)

    # Latency tracking
    first_response_latency: Optional[float] = None
    avg_response_latency: float = 0.0
    response_count: int = 0

    # Events
    events: list = field(default_factory=list)


class CostCalculator:
    """Calculate costs based on OpenAI pricing"""

    # OpenAI Pricing (as of 2025)
    PRICES = {
        # Whisper STT
        "whisper": 0.006,  # $0.006 per minute

        # GPT-4o-mini
        "gpt-4o-mini-input": 0.150 / 1_000_000,  # $0.15 per 1M tokens
        "gpt-4o-mini-output": 0.600 / 1_000_000,  # $0.60 per 1M tokens

        # TTS
        "tts-1": 15.00 / 1_000_000,  # $15 per 1M characters
        "tts-1-hd": 30.00 / 1_000_000,  # $30 per 1M characters
    }

    @staticmethod
    def calculate_stt_cost(audio_seconds: float) -> float:
        """Calculate STT cost in USD"""
        minutes = audio_seconds / 60
        return minutes * CostCalculator.PRICES["whisper"]

    @staticmethod
    def calculate_llm_cost(input_tokens: int, output_tokens: int) -> float:
        """Calculate LLM cost in USD"""
        input_cost = input_tokens * CostCalculator.PRICES["gpt-4o-mini-input"]
        output_cost = output_tokens * CostCalculator.PRICES["gpt-4o-mini-output"]
        return input_cost + output_cost

    @staticmethod
    def calculate_tts_cost(characters: int, hd: bool = False) -> float:
        """Calculate TTS cost in USD"""
        price = CostCalculator.PRICES["tts-1-hd" if hd else "tts-1"]
        return characters * price

    @staticmethod
    def calculate_total_cost(metrics: CallMetrics) -> Dict:
        """Calculate total cost breakdown"""
        stt_cost = CostCalculator.calculate_stt_cost(metrics.stt_seconds)
        llm_cost = CostCalculator.calculate_llm_cost(
            metrics.llm_input_tokens,
            metrics.llm_output_tokens
        )
        tts_cost = CostCalculator.calculate_tts_cost(metrics.tts_characters)

        total = stt_cost + llm_cost + tts_cost
        duration_minutes = (time.time() - metrics.start_time) / 60
        cost_per_minute = total / duration_minutes if duration_minutes > 0 else 0

        return {
            "breakdown": {
                "stt": round(stt_cost, 4),
                "llm": round(llm_cost, 4),
                "tts": round(tts_cost, 4),
            },
            "total": round(total, 4),
            "duration_minutes": round(duration_minutes, 2),
            "cost_per_minute": round(cost_per_minute, 4),
            "usage": {
                "stt_seconds": round(metrics.stt_seconds, 1),
                "llm_input_tokens": metrics.llm_input_tokens,
                "llm_output_tokens": metrics.llm_output_tokens,
                "tts_characters": metrics.tts_characters,
                "tool_calls": metrics.tool_calls,
            }
        }


class MetricsTracker:
    """Global metrics tracker"""

    def __init__(self):
        self.active_calls: Dict[str, CallMetrics] = {}
        self.completed_calls: list = []

    def start_call(self, call_id: str) -> CallMetrics:
        """Start tracking a new call"""
        metrics = CallMetrics(call_id=call_id)
        self.active_calls[call_id] = metrics
        logger.info(f"📊 Started tracking metrics for call {call_id}")
        return metrics

    def log_event(self, call_id: str, event_type: str, data: Dict = None):
        """Log an event with timestamp"""
        if call_id not in self.active_calls:
            return

        event = {
            "timestamp": time.time(),
            "type": event_type,
            "data": data or {}
        }
        self.active_calls[call_id].events.append(event)

        # Log detailed event
        if event_type == "tool_call":
            logger.info(f"🔧 Tool called: {data.get('tool_name')} | Call: {call_id}")
        elif event_type == "agent_speaking":
            logger.info(f"🗣️ Agent speaking: {data.get('characters', 0)} chars | Call: {call_id}")
        elif event_type == "user_speaking":
            logger.info(f"🎤 User speaking: {data.get('duration', 0):.1f}s | Call: {call_id}")

    def update_stt(self, call_id: str, seconds: float):
        """Update STT usage"""
        if call_id in self.active_calls:
            self.active_calls[call_id].stt_seconds += seconds

    def update_llm(self, call_id: str, input_tokens: int, output_tokens: int):
        """Update LLM usage"""
        if call_id in self.active_calls:
            self.active_calls[call_id].llm_input_tokens += input_tokens
            self.active_calls[call_id].llm_output_tokens += output_tokens

    def update_tts(self, call_id: str, characters: int):
        """Update TTS usage"""
        if call_id in self.active_calls:
            self.active_calls[call_id].tts_characters += characters
            self.log_event(call_id, "agent_speaking", {"characters": characters})

    def record_tool_call(self, call_id: str, tool_name: str, duration: float):
        """Record a tool call"""
        if call_id in self.active_calls:
            metrics = self.active_calls[call_id]
            metrics.tool_calls += 1
            metrics.tool_call_times.append(duration)
            self.log_event(call_id, "tool_call", {
                "tool_name": tool_name,
                "duration": duration
            })

    def record_response_latency(self, call_id: str, latency: float):
        """Record response latency"""
        if call_id in self.active_calls:
            metrics = self.active_calls[call_id]

            if metrics.first_response_latency is None:
                metrics.first_response_latency = latency
                logger.info(f"⚡ First response latency: {latency:.2f}s | Call: {call_id}")

            # Calculate running average
            total = metrics.avg_response_latency * metrics.response_count + latency
            metrics.response_count += 1
            metrics.avg_response_latency = total / metrics.response_count

    def end_call(self, call_id: str) -> Dict:
        """End call tracking and return final metrics"""
        if call_id not in self.active_calls:
            return {}

        metrics = self.active_calls.pop(call_id)
        cost_info = CostCalculator.calculate_total_cost(metrics)

        # Add performance metrics
        performance = {
            "first_response_latency": round(metrics.first_response_latency, 2) if metrics.first_response_latency else None,
            "avg_response_latency": round(metrics.avg_response_latency, 2),
            "total_responses": metrics.response_count,
            "avg_tool_call_time": round(
                sum(metrics.tool_call_times) / len(metrics.tool_call_times), 2
            ) if metrics.tool_call_times else 0,
        }

        result = {
            **cost_info,
            "performance": performance,
            "call_id": call_id,
            "duration_seconds": round(time.time() - metrics.start_time, 1),
        }

        self.completed_calls.append(result)

        # Log summary
        logger.info(f"""
📊 Call Metrics Summary - {call_id}
├─ Duration: {result['duration_minutes']:.2f} min
├─ Total Cost: ${result['total']:.4f}
├─ Cost/Minute: ${result['cost_per_minute']:.4f}
├─ STT: {result['breakdown']['stt']:.4f} ({cost_info['usage']['stt_seconds']}s)
├─ LLM: ${result['breakdown']['llm']:.4f} ({cost_info['usage']['llm_input_tokens']} in / {cost_info['usage']['llm_output_tokens']} out)
├─ TTS: ${result['breakdown']['tts']:.4f} ({cost_info['usage']['tts_characters']} chars)
├─ Tool Calls: {cost_info['usage']['tool_calls']}
├─ First Response: {performance['first_response_latency']}s
└─ Avg Response: {performance['avg_response_latency']:.2f}s
        """)

        return result

    def get_stats(self) -> Dict:
        """Get overall statistics"""
        if not self.completed_calls:
            return {"message": "No completed calls yet"}

        total_cost = sum(call['total'] for call in self.completed_calls)
        total_duration = sum(call['duration_minutes'] for call in self.completed_calls)
        avg_cost_per_minute = total_cost / total_duration if total_duration > 0 else 0

        return {
            "total_calls": len(self.completed_calls),
            "total_cost": round(total_cost, 4),
            "total_duration_minutes": round(total_duration, 2),
            "avg_cost_per_minute": round(avg_cost_per_minute, 4),
            "avg_cost_per_call": round(total_cost / len(self.completed_calls), 4),
        }


# Global tracker instance
metrics_tracker = MetricsTracker()
