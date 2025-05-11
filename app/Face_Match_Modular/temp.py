import cv2, face_recognition

# 1) load
img = cv2.imread(r"D:/face_recognition_surveillance_final/temp_frames/CAM1_frame_20250509_210109638307.jpg")

# 2) upscale by 2× (now ~1224×816)
img_up = cv2.resize(img, (0,0), fx=2.0, fy=2.0)

# 3) detect on the larger image
rgb_up = cv2.cvtColor(img_up, cv2.COLOR_BGR2RGB)
locs_up = face_recognition.face_locations(
    rgb_up,
    model="hog",
    number_of_times_to_upsample=2
)

print("Upscaled – found", len(locs_up), "faces:", locs_up)

# 4) if you want to draw boxes on the original:
for top, right, bottom, left in locs_up:
    # convert from upscaled coords back to original
    t, r, b, l = top//2, right//2, bottom//2, left//2
    cv2.rectangle(img, (l, t), (r, b), (0,255,0), 2)

cv2.imwrite(r"D:/face_recognition_surveillance_final/temp_frames/debug_upscaled.jpg", img)