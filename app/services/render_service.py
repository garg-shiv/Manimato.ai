import os
import shutil
import subprocess
import uuid


from core.config import config


def cleanup_manim_files(script_filename:str):
    """
    Clean up unnecessary files created during Manim rendering.
    
    Args:
        script_filename: The base filename (without extension) used for the script
    """
    media_dir = config.MEDIA_DIR

    # 1. Remove media/videos/<script_filename> directories 
    videos_dir = os.path.join(media_dir,"videos")
    if os.path.exists(videos_dir):
        script_video_dir = os.path.join(videos_dir,script_filename)
        if os.path.exists(script_video_dir):
            shutil.rmtree(script_video_dir,ignore_errors=True)
            print(f"Removed video directory: {script_video_dir}")
        
    # 2. Remove media/images/<script_filename directories
    images_dir = os.path.join(media_dir,"images")

    if os.path.exists(images_dir):
        script_image_dir = os.path.join(images_dir,script_filename)
        if os.path.exists(script_image_dir):
            shutil.rmtree(script_image_dir,ignore_errors=True)
            print(f"Removed images directory: {script_image_dir}")

    # 3. Remove Script-specific .pyc flies (only those related to our script)
    generated_dir = config.GENERATED_DIR
    pycache_dir = os.path.join(generated_dir,"__pycache__")
    if os.path.exists(pycache_dir):
        for cache_file in os.listdir(pycache_dir):
            if cache_file.startswith(f"{script_filename}.cpython-") and cache_file.endswith(".pyc"):
                cache_file_path = os.path.join(pycache_dir,cache_file)

                os.remove(cache_file_path)

                print(f"Removed cache file: {cache_file_path}")



    print(f"Cleanup completed for script: {script_filename}")





def render_manim_script(script: str) -> str:
    output_dir = config.GENERATED_DIR
    script_filename = f"script_{uuid.uuid4().hex[:8]}"
    script_path = os.path.join(output_dir, f"{script_filename}.py")

    with open(script_path, "w") as f:
        f.write(script)

    try:
        subprocess.run(
            ["manim", script_path, "GenScene", "-qk", "--output_file", f"{script_filename}.mp4"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )

        # Manim saves to media/videos/<scene_id>/.../output.mp4, so we locate it
        media_dir = os.path.join(config.MEDIA_DIR, "videos")
        final_output_path = None

        for root, _, files in os.walk(media_dir):
            for file in files:
                if file == f"{script_filename}.mp4":
                    manim_output_path = os.path.join(root, file)
                    final_output_path = os.path.join(
                        output_dir, f"{script_filename}_output.mp4"
                    )
                    shutil.copyfile(manim_output_path, final_output_path)
                   
                    return final_output_path

        raise FileNotFoundError(f"{script_filename}.mp4 not found in media directory.")

    except subprocess.CalledProcessError as e:
        print("Manim rendering failed:", e.stderr)

        raise RuntimeError("Rendering failed") from e

    finally:
        if os.path.exists(script_path):
            os.remove(script_path)
        
        #CLEANUP: remove all unecessary files after successful generation
        cleanup_manim_files(script_filename)


