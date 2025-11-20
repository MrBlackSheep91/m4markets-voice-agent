"""
Langfuse Integration for M4Markets Voice Agent
Comprehensive observability and cost tracking with Langfuse
"""

import os
import time
import logging
from typing import Dict, Optional, List
from langfuse import Langfuse
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Initialize Langfuse client
langfuse = None

def init_langfuse():
    """Initialize Langfuse client with credentials from env"""
    global langfuse

    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    host = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

    if not public_key or not secret_key:
        logger.warning("⚠️ Langfuse credentials not found - observability disabled")
        return None

    try:
        langfuse = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
        logger.info(f"✅ Langfuse initialized - Host: {host}")
        return langfuse
    except Exception as e:
        logger.error(f"❌ Failed to initialize Langfuse: {str(e)}")
        return None


class VoiceCallTracer:
    """Traces voice calls with Langfuse"""

    def __init__(self, call_id: str, user_phone: Optional[str] = None):
        """
        Initialize tracer for a voice call

        Args:
            call_id: Unique identifier for the call
            user_phone: Phone number of the lead (optional)
        """
        self.call_id = call_id
        self.user_phone = user_phone
        self.trace = None
        self.current_generation = None
        self.start_time = time.time()

        if langfuse:
            # Create trace using SDK v3 API
            try:
                trace_data = {
                    "name": "voice_call",
                    "userId": user_phone,
                    "sessionId": call_id,
                    "metadata": {
                        "call_type": "voice",
                        "platform": "livekit",
                        "agent": "m4markets-sales"
                    }
                }
                self.trace = langfuse.trace(**trace_data)
                logger.info(f"📊 Langfuse trace started: {call_id}")
            except Exception as e:
                logger.warning(f"⚠️ Failed to create Langfuse trace: {str(e)}")
                self.trace = None

    def track_stt(self, audio_duration: float, text: str):
        """Track Speech-to-Text generation"""
        if not self.trace:
            return

        try:
            self.trace.generation(
                name="speech_to_text",
                model="whisper-1",
                input=f"Audio: {audio_duration:.1f}s",
                output=text,
                metadata={
                    "duration_seconds": audio_duration,
                    "provider": "openai"
                },
                usage={
                    "unit": "seconds",
                    "input": int(audio_duration),
                    "total": int(audio_duration)
                },
                usage_details={
                    "input_cost": audio_duration * 0.0001,  # $0.006/min
                }
            )
            logger.debug(f"🎤 STT tracked: {audio_duration:.1f}s")
        except Exception as e:
            logger.error(f"Error tracking STT: {str(e)}")

    def start_llm_generation(self, messages: List[Dict]):
        """Start tracking an LLM generation"""
        if not self.trace:
            return None

        try:
            self.current_generation = self.trace.generation(
                name="llm_reasoning",
                model="gpt-4o-mini",
                input=messages,
                metadata={
                    "provider": "openai",
                    "temperature": 0.7
                }
            )
            return self.current_generation
        except Exception as e:
            logger.error(f"Error starting LLM generation: {str(e)}")
            return None

    def end_llm_generation(self, output: str, input_tokens: int, output_tokens: int):
        """End tracking an LLM generation"""
        if not self.current_generation:
            return

        try:
            # Calculate costs (GPT-4o-mini pricing)
            input_cost = input_tokens * 0.15 / 1_000_000
            output_cost = output_tokens * 0.60 / 1_000_000

            self.current_generation.update(
                output=output,
                usage={
                    "input": input_tokens,
                    "output": output_tokens,
                    "total": input_tokens + output_tokens
                },
                usage_details={
                    "input_cost": input_cost,
                    "output_cost": output_cost,
                    "total_cost": input_cost + output_cost
                }
            )

            self.current_generation.end()
            logger.debug(f"🧠 LLM tracked: {input_tokens} in / {output_tokens} out")
        except Exception as e:
            logger.error(f"Error ending LLM generation: {str(e)}")
        finally:
            self.current_generation = None

    def track_tts(self, text: str, audio_duration: float, characters: int):
        """Track Text-to-Speech generation"""
        if not self.trace:
            return

        try:
            # TTS pricing: $15 per 1M characters
            cost = characters * 15 / 1_000_000

            self.trace.generation(
                name="text_to_speech",
                model="tts-1-nova",
                input=text,
                output=f"Audio: {audio_duration:.1f}s",
                metadata={
                    "voice": "nova",
                    "speed": 1.15,
                    "provider": "openai",
                    "characters": characters
                },
                usage={
                    "unit": "characters",
                    "input": characters,
                    "total": characters
                },
                usage_details={
                    "input_cost": cost,
                }
            )
            logger.debug(f"🗣️ TTS tracked: {characters} chars")
        except Exception as e:
            logger.error(f"Error tracking TTS: {str(e)}")

    def track_tool_call(self, tool_name: str, input_params: Dict, output: any, duration: float):
        """Track a tool/function call"""
        if not self.trace:
            return

        try:
            span = self.trace.span(
                name=f"tool_{tool_name}",
                input=input_params,
                output=output,
                metadata={
                    "tool_type": "function",
                    "duration_seconds": duration
                }
            )
            span.end()
            logger.debug(f"🔧 Tool tracked: {tool_name} ({duration:.2f}s)")
        except Exception as e:
            logger.error(f"Error tracking tool call: {str(e)}")

    def set_tags(self, tags: List[str]):
        """Set tags for the trace"""
        if self.trace:
            try:
                self.trace.update(tags=tags)
            except Exception as e:
                logger.error(f"Error setting tags: {str(e)}")

    def set_metadata(self, metadata: Dict):
        """Update trace metadata"""
        if self.trace:
            try:
                current_metadata = self.trace.metadata or {}
                current_metadata.update(metadata)
                self.trace.update(metadata=current_metadata)
            except Exception as e:
                logger.error(f"Error setting metadata: {str(e)}")

    def end_trace(self, outcome: str, final_metadata: Optional[Dict] = None):
        """End the trace with final outcome"""
        if not self.trace:
            return

        try:
            duration = time.time() - self.start_time

            metadata = {
                "outcome": outcome,
                "duration_seconds": duration,
                "call_id": self.call_id
            }

            if final_metadata:
                metadata.update(final_metadata)

            self.trace.update(
                metadata=metadata,
                output={"outcome": outcome, "duration": duration}
            )

            logger.info(f"✅ Langfuse trace completed: {self.call_id} | Outcome: {outcome}")
        except Exception as e:
            logger.error(f"Error ending trace: {str(e)}")


# Context manager for tool tracking
@contextmanager
def track_tool_execution(tracer: VoiceCallTracer, tool_name: str, input_params: Dict):
    """Context manager to automatically track tool execution"""
    start_time = time.time()
    result = None
    error = None

    try:
        yield
    except Exception as e:
        error = e
        raise
    finally:
        duration = time.time() - start_time
        if tracer and tracer.trace:
            output = {"error": str(error)} if error else {"success": True}
            tracer.track_tool_call(tool_name, input_params, output, duration)


# Initialize on module import
init_langfuse()
