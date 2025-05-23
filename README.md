# Phoenix OTEL Demo: LLM & Base OTEL Tracing

This repository contains a Python script demonstrating the use of `phoenix-otel` for instrumenting both LLM-specific operations using [Arize Phoenix](https://docs.arize.com/phoenix) and [base OpenTelemetry](https://opentelemetry.io/) (OTEL) traces within a single application.

The goal is to showcase the flexibility of `phoenix-otel` and the visualization of mixed traces (LLM-focused and standard OTEL) in the Phoenix UI.

> ✅ **Tested on Python 3.11**

## Key Features

* **Hybrid Tracing:** Demonstrates the co-existence and visualization of LLM-specific spans (`CHAIN`, `LLM`, `TOOL`) alongside standard OTEL spans (`INTERNAL`, `SERVER`).
* **Phoenix OTEL Instrumentation:** Shows usage of decorators (`@tracer.chain`, etc.) and context managers (`with tracer.start_as_current_span(...)`) provided by `phoenix-otel`.
* **Base OpenTelemetry:** Includes examples of creating standard OTEL spans with different `SpanKind` values and custom attributes.
* **Nested Spans:** Creates parent-child span relationships to build complete trace visualizations.
* **Auto-Instrumentation:** Leverages `phoenix-otel`'s auto-instrumentation capabilities (e.g., for OpenAI calls, if configured).
* **Sync & Async:** Includes examples for instrumenting both synchronous and asynchronous Python functions using base OTEL.
* **Environment-Based Configuration:** Uses environment variables (optionally loaded from a `.env` file) for secure and flexible setup.

## Setup

1. Ensure your Phoenix server/UI is running.

   ```bash
   docker run -p 6006:6006 -p 4317:4317 -i -t arizephoenix/phoenix:latest
   ```

2. Navigate to [http://0.0.0.0:6006](http://0.0.0.0:6006) and you should see your local Arize Phoenix
3. Clone the Repository:

    ```bash
    git clone git@github.com:vbelouso/phoenix-otel.git
    cd phoenix-otel
    ```

4. Create a Virtual Environment:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

5. Install Dependencies:

    ```bash
    pip install -r requirements.txt
    ```

6. **Configure Environment Variables:**
    * Configuration is primarily handled via environment variables, optionally loaded from a `.env` file using `python-dotenv`.
    * **Important:** If using a `.env` file, create it in the project root.
    * You **must** set `OPENAI_API_KEY` correctly (either as a system environment variable or in `.env`) if you intend for the `llm_tracing()` function to successfully call the OpenAI API. The other variables have defaults provided in the script but can be overridden.
    * The script uses the following environment variables:

        | Variable                     | Description                                     | Default Value (in script)         | Required?                                |
        | :--------------------------- | :---------------------------------------------- | :-------------------------------- | :--------------------------------------- |
        | `OPENAI_API_KEY`             | Your OpenAI API key.                            | `"PLACEHOLDER"`                   | **Yes**, if making actual LLM calls.     |
        | `PHOENIX_PROJECT_NAME`       | The project name to use in Phoenix.             | `"phoenix-otel"`                  | No (uses default, adjust if needed)      |
        | `PHOENIX_COLLECTOR_ENDPOINT` | The OTLP HTTP endpoint(including `/v1/traces`). | `"http://0.0.0.0:6006/v1/traces"` | No (uses default, adjust if needed)      |
        | `OPENAI_BASE_URL`            | Optional base URL for the OpenAI client.        | `None`                            | Only if needed (depends on OpenAI setup) |

    * Alternative Methods: You can set environment variables directly in your terminal.

## Running the Script

1. Ensure your virtual environment is activated (`source .venv/bin/activate`).
2. Make sure the necessary environment variables are set (either system-wide or via the `.env` file).
3. Run the Python script:

    ```bash
    python phoenix_otel.py
    ```

## Viewing Results

1. Open the [Phoenix UI](http://0.0.0.0:6006) in your web browser.
2. Navigate to the project specified by `PHOENIX_PROJECT_NAME`.
3. You should see the traces generated by the script, including:
    * Spans created by Phoenix decorators (`LLM`, `CHAIN`, `TOOL`).
    * Spans created using `with tracer.start_as_current_span(...)` with `openinference_span_kind`.
    * Spans automatically generated by OpenAI auto-instrumentation (if run and configured).
    * Standard OTEL spans (`INTERNAL`, `SERVER`) will be shown with `Kind: Unknown` in the UI due to current Phoenix backend behavior. You can identify these by their names.
    * Nested span structures showing parent-child relationships.
