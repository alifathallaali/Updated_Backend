class PharmaLensError(Exception):
    pass

class ContractError(PharmaLensError):
    pass

class EngineNotFoundError(PharmaLensError):
    pass

class TaskExecutionError(PharmaLensError):
    pass
