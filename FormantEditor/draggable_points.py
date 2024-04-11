class DraggablePoint:
    def __init__(self, point, canvas, on_delete, on_drag_complete=None):
        self.point = point
        self.canvas = canvas
        self.on_delete_callback = on_delete
        self.on_drag_complete_callback = on_drag_complete
        self.press = None
        self.on_delete_callback = on_delete
        # Event connections
        self.cidpress = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)
        # Visual guides
        self.vline = None
        self.hline = None


    def on_release_draggable_point(self, event):
        # Existing code to handle point release
        if self.on_drag_end:
            self.on_drag_end()  # Call the callback function after dragging is done

    def on_press(self, event):
        if event.inaxes != self.point.axes or event.button != 1: return
        contains, attrd = self.point.contains(event)
        if not contains: return
        x0, y0 = self.point.get_data()
        self.press = x0, y0, event.xdata, event.ydata
        # Create or update guide lines
        self.vline = self.canvas.axes.axvline(x=x0, color='gray', linestyle='--')
        self.hline = self.canvas.axes.axhline(y=y0, color='gray', linestyle='--')
        self.canvas.draw_idle()

    def on_motion(self, event):
        if self.press is None: return
        x0, y0, _, _ = self.press
        if event.inaxes != self.point.axes: return
        # Update only the Y position of the point and the horizontal line
        self.point.set_data(x0, event.ydata)
        self.hline.set_ydata(event.ydata)  # Update horizontal line position
        # Keep vertical line at the initial x position
        self.vline.set_xdata(x0)
        self.canvas.draw_idle()

    def on_release(self, event):
        if self.press is None: return
        self.press = None
        # Remove guide lines
        if self.vline is not None and self.hline is not None:
            self.vline.remove()
            self.hline.remove()
        self.canvas.draw_idle()
        self.canvas.end_dragging_point()
        if self.press is None: return
        self.press = None
        self.canvas.draw_idle()
        self.canvas.end_dragging_point()  # Assuming this method signals the end of dragging
        if self.on_drag_complete_callback:  # Check if the callback is provided
            self.on_drag_complete_callback()  # Call the callback

    def on_right_click(self, event):
        if event.button != 3: return
        contains, attrd = self.point.contains(event)
        if not contains: return
        self.on_delete_callback(self)
