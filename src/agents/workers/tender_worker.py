from src.core.contracts import EngineResult, ResultMetadata

def run_tender_task(parameters):
    from src.tender.tender_engine import analyze_tender
    data = analyze_tender(parameters)
    return EngineResult.success(
        tool="tender_tool",
        data=data,
        metadata=ResultMetadata(
            engine="tender_engine",
            data_source=parameters.get("data_source"),
        ),
    )
