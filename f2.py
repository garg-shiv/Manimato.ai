
import os
import subprocess
import uuid

def render_manim_script(script_code: str, class_name="GenScene") -> str:
    # Create unique file names
    script_id = uuid.uuid4().hex[:8]
    script_file = f"generated/script_{script_id}.py"
    output_video = f"generated/output_{script_id}.mp4"

    # Write the script to a file
    os.makedirs("generated", exist_ok=True)
    with open(script_file, "w", encoding="utf-8") as f:
        f.write(script_code)

    # Run the Manim command in a subprocess with timeout
    try:
        subprocess.run(
            ["manim", script_file, class_name, "-o", output_video],
            timeout=60,
            check=True
        )
    except subprocess.CalledProcessError:
        raise RuntimeError("Manim rendering failed.")
    except subprocess.TimeoutExpired:
        raise RuntimeError("Rendering took too long and timed out.")

    return output_video
