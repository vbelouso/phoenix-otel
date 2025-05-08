import os

import openai
from dotenv import load_dotenv
from opentelemetry.trace import SpanKind
from opentelemetry.trace.status import Status, StatusCode
from phoenix.otel import register

load_dotenv()

PHOENIX_PROJECT_NAME = os.getenv("PHOENIX_PROJECT_NAME", "phoenix-otel")
PHOENIX_COLLECTOR_ENDPOINT = os.getenv(
    "PHOENIX_COLLECTOR_ENDPOINT", "http://0.0.0.0:6006/v1/traces"
)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "PLACEHOLDER")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
tracer_provider = register(
    endpoint=PHOENIX_COLLECTOR_ENDPOINT,
    protocol="http/protobuf",
    project_name=PHOENIX_PROJECT_NAME,
    auto_instrument=True,
    batch=True,
)
tracer = tracer_provider.get_tracer(__name__)

client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)


@tracer.chain
def chain_tracer(input_data: str) -> str:
    return f"Output from chain_tracer: {input_data}"


@tracer.llm
def llm_tracer(input_data: str) -> dict:
    return {"model_output": f"Output from llm_tracer: {input_data}"}


@tracer.tool
def tool_tracer(input_data: str):
    return f"Output from tool_tracer: {input_data}"


@tracer.chain(name="nested_phoenix_otel")
def nested_phoenix_otel():
    chain_tracer("input_for_chain")
    llm_tracer("input_for_llm")
    tool_tracer("input_for_tool")


@tracer.chain(name="nested_spans_with_clause")
def nested_spans_with_clause(input_str: str) -> str:
    with tracer.start_as_current_span(
        "nested_span_child", openinference_span_kind="chain"
    ) as child_span:
        child_span.set_input(input_str)
        child_span.set_output("Output")
        child_span.set_status(Status(StatusCode.OK))
        with tracer.start_as_current_span(
            "nested_span_child_tool", openinference_span_kind="tool"
        ) as tool_span:
            tool_span.set_input(input_str)
            tool_span.set_output("Output")
            tool_span.set_status(Status(StatusCode.OK))
            with tracer.start_as_current_span(
                "llm_call", openinference_span_kind="llm"
            ) as llm_span:
                llm_span.set_input(input_str)
                llm_span.set_output("Output")
                llm_span.set_status(Status(StatusCode.OK))
                with tracer.start_as_current_span(
                    "child", kind=SpanKind.INTERNAL
                ) as child:
                    child.set_attribute("operation.name", "Saying hello!")
                    child.set_attribute("openinference.span.kind", "INTERNAL")
    return "nested span end"


def llm_tracing():
    try:
        response = client.chat.completions.create(
            model="hugging-quants/Meta-Llama-3.1-70B-Instruct-AWQ-INT4",
            messages=[{"role": "user", "content": "Write a haiku."}],
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error calling OpenAI: {e}")


def vanilla_otel_sync_level3(data: str) -> str:
    with tracer.start_as_current_span(
        "vanilla_sync_level3_process", kind=SpanKind.INTERNAL
    ) as span:
        span.set_attribute("input.data", data)
        result = f"Processed by L3: {data}"
        span.set_attribute("output.data", result)
        span.set_attribute("openinference.span.kind", "INTERNAL")
        return result


def vanilla_otel_sync_level2(data: str) -> str:
    with tracer.start_as_current_span(
        "vanilla_sync_level2_delegate", kind=SpanKind.INTERNAL
    ) as span:
        span.set_attribute("input.data", data)
        result_from_l3 = vanilla_otel_sync_level3(data + " from L2")
        span.set_attribute("result.from.l3", result_from_l3)
        span.set_attribute("openinference.span.kind", "INTERNAL")
        return f"Processed by L2: {result_from_l3}"


def vanilla_otel_sync_main(initial_data: str) -> str:
    with tracer.start_as_current_span(
        "vanilla_sync_main_operation", kind=SpanKind.SERVER
    ) as span:
        span.set_attribute("initial.data", initial_data)
        final_result = vanilla_otel_sync_level2(initial_data + " from Main")
        span.set_attribute("final.result", final_result)
        span.set_status(Status(StatusCode.OK))
        span.set_attribute("openinference.span.kind", "SERVER")
        return final_result


def run_all_sync():
    vanilla_otel_sync_main("start vanilla_otel_sync_main")


if __name__ == "__main__":
    try:
        print("🔱 Run run_all_sync")
        run_all_sync()
        print("🔱 Run nested_spans_with_clause")
        nested_spans_with_clause("nested_spans_with_clause")
        print("🔱 Run nested_phoenix_otel")
        nested_phoenix_otel()
        print("🔱 Run llm_tracing (for Auto-Instrumentation)")
        llm_tracing()
    finally:
        tracer_provider.shutdown()
        print("✅ Done")
