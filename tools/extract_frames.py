import cv2
import os
import sys

video_path = "../assets/video/Gerar_um_video_202604171619.mp4"
output_dir = "../templates/hero-frames"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"Opening video: {video_path}")
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    print(f"Error: Failed to open video {video_path}")
    sys.exit(1)

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS)
print(f"Detected {total_frames} frames at {fps} FPS.")

frame_idx = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Save as highly compressed WebP to ensure fast network loading 
    # and minimal memory usage in browser canvas
    out_path = os.path.join(output_dir, f"frame_{frame_idx:04d}.webp")
    
    # Using cv2.IMWRITE_WEBP_QUALITY at 75% 
    cv2.imwrite(out_path, frame, [int(cv2.IMWRITE_WEBP_QUALITY), 75])
    
    frame_idx += 1
    if frame_idx % 50 == 0:
        print(f"Extracted {frame_idx}/{total_frames} frames...")

cap.release()
print(f"SUCCESS: Extracted {frame_idx} frames to {output_dir}")
