# Example Integration with main.py

Here's how to integrate the custom error system into your existing FastAPI app:

## 1. Update main.py

```python
# Add this import at the top
from app.error_handler import add_error_handlers

# After creating your FastAPI app
app = FastAPI(
    title="Manim Code Generator API",
    description="API for generating Manim animations from natural language prompts",
    version="1.0.0",
)

# Add CORS middleware
add_cors_middleware(app)
# Add request logger middleware  
add_request_logger_middleware(app)

# ADD THIS: Add error handlers
add_error_handlers(app)

# Include routers
app.include_router(v1_router, prefix="/api")
app.include_router(health_router)
```

## 2. Update your routes to use custom errors

```python
# In your route files, for example auth/routes.py
from app.error_handler import CustomError, auth_error, log_info, log_error

@router.post("/login")
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = get_user_by_email(db, credentials.email)
        if not user:
            raise auth_error("User not found", email=credentials.email)
        
        if not verify_password(credentials.password, user.password_hash):
            raise auth_error("Invalid password", user_id=user.id)
        
        token = create_access_token({"user_id": user.id})
        
        log_info("User logged in successfully", user_id=user.id, email=credentials.email)
        
        return {"access_token": token, "token_type": "bearer"}
        
    except CustomError:
        # Re-raise custom errors (they'll be handled by the error handler)
        raise
    except Exception as e:
        # Convert unexpected errors
        log_error("Login failed with unexpected error", str(e), email=credentials.email)
        raise CustomError(
            message=f"Login failed: {str(e)}",
            error_code="LOGIN_ERROR", 
            context={"email": credentials.email}
        )
```

## 3. Example usage in video generation

```python
# In videos/routes.py
from app.error_handler import CustomError, validation_error, server_error, log_info

@router.post("/generate")
async def generate_video(request: VideoRequest):
    try:
        if not request.prompt.strip():
            raise validation_error("Prompt cannot be empty", field="prompt")
        
        if len(request.prompt) > 1000:
            raise validation_error("Prompt too long", field="prompt", max_length=1000)
        
        log_info("Starting video generation", prompt_length=len(request.prompt))
        
        # Your video generation logic here
        video_path = generate_manim_video(request.prompt)
        
        log_info("Video generated successfully", video_path=video_path)
        
        return {"video_url": video_path, "status": "completed"}
        
    except CustomError:
        raise
    except Exception as e:
        raise server_error(f"Video generation failed: {str(e)}", prompt=request.prompt)
```

This simple system gives you:
- ✅ Easy error creation and handling
- ✅ Automatic logging with context
- ✅ Consistent API error responses  
- ✅ Unique error IDs for tracking
- ✅ Better debugging information
- ✅ Minimal code changes needed
