from window import Window

window = Window(670,600, "Jetson Stereo Tuner")
window.draw_buttons()
window.DM_video_cap()
window.run()