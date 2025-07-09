import os
import shutil
import subprocess
import uuid


def render_manim_script(script: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "..", "..", "generated")
    os.makedirs(output_dir, exist_ok=True)

    script_filename = f"script_{uuid.uuid4().hex[:8]}.py"
    script_path = os.path.join(output_dir, script_filename)

    with open(script_path, "w") as f:
        f.write(script)

    try:
        subprocess.run(
            ["manim", script_path, "GenScene", "-qk", "--output_file", "output.mp4"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8", 
        )

        # Manim saves to media/videos/<scene_id>/.../output.mp4, so we locate it
        media_dir = os.path.join(base_dir, "..", "..", "media", "videos")
        final_output_path = None

        for root, _, files in os.walk(media_dir):
            for file in files:
                if file == "output.mp4":
                    manim_output_path = os.path.join(root, file)
                    final_output_path = os.path.join(
                        output_dir, f"{uuid.uuid4().hex[:8]}_output.mp4"
                    )
                    shutil.copyfile(manim_output_path, final_output_path)
                    return final_output_path

        raise FileNotFoundError("output.mp4 not found in media directory.")

    except subprocess.CalledProcessError as e:
        print("Manim rendering failed:", e.stderr)
        raise RuntimeError("Rendering failed") from e

    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
