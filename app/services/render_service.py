import os
import subprocess
import uuid

def render_manim_script(script: str) -> str:
    # Define the output folder relative to this script
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "..", "..", "generated")
    os.makedirs(output_dir, exist_ok=True)

    # Generate unique script filename
    script_filename = f"script_{uuid.uuid4().hex[:8]}.py"
    script_path = os.path.join(output_dir, script_filename)

    # Write script to file
    with open(script_path, "w") as f:
        f.write(script)

    try:
        # Call Manim subprocess to render the video
        result = subprocess.run(
            ["manim", script_path, "GenScene", "-qk", "--output_file", "output.mp4"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        print("✅ Manim rendering succeeded.")
        print("STDOUT:\n", result.stdout)

        output_path = os.path.join(output_dir, "output.mp4")
        return output_path

    except subprocess.CalledProcessError as e:
        print("❌ Manim rendering failed.")
        print("STDOUT:\n", e.stdout)
        print("STDERR:\n", e.stderr)
        raise RuntimeError("Manim rendering failed.") from e

    finally:
        # Clean up script file
        if os.path.exists(script_path):
            os.remove(script_path)
