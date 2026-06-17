from fastapi import HTTPException

def not_found(message: str):
    raise HTTPException(status_code=404, detail={'error': 'not_found', 'message': message})

def bad_request(message: str):
    raise HTTPException(status_code=400, detail={'error': 'bad_request', 'message': message})
