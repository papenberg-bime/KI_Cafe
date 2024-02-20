import threading
import queue
import time
import tkinter
from tkinter import ttk

thread_queue = queue.Queue()
def thread_target(test):
	for number in range(10):
		print("thread hello to queue ", test)
		thread_queue.put("hello " + str(number))
		time.sleep(1)
	thread_queue.put(None)

  
def after_callback():
	try:
		message = thread_queue.get(block=False)
	except queue.Empty:
		root.after(100, after_callback)
		return

	print("Got message", message)
	if message is not None:
		label['text'] = message
		root.after(100, after_callback)
	else:
		root.quit()

  
root = tkinter.Tk()
frame = ttk.Frame(root)
frame.pack(fill='both',expand=True)

label = ttk.Label(frame)
label.pack()

threading.Thread(target=thread_target,kwargs={"test":"Argument to thread"}).start()
root.after(100, after_callback)

root.geometry('200x200')
root.mainloop()