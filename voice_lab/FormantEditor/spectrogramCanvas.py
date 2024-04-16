import sys
from PyQt5.QtWidgets import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.patches import Rectangle
from create_formant_data_for_formant_editor import MeasureFormants
from draggable_points import DraggablePoint
import numpy as np
from statsmodels.nonparametric.smoothers_lowess import lowess



class SpectrogramCanvas(FigureCanvas):
    def __init__(self, parent=None, dpi=100):
        fig = Figure(dpi=dpi)  # Create a Figure instance.
        self.axes = fig.add_subplot(111)  # Add a subplot to the figure.

        # Initialize the FigureCanvas with the Figure object.
        super(SpectrogramCanvas, self).__init__(fig)
        self.setParent(parent)
        self.is_dragging_point = False  

        # Initialize the measurements attribute with an instance of MeasureFormants.
        self.measurements = MeasureFormants()  # Assuming MeasureFormants provides the draw_spectrogram method.
        self.measurements.load_sound()  # Load the sound data.

        # Initialize draggable_points as an empty list.
        self.draggable_points = []  # This will store instances of DraggablePoint.

        # Compute the initial figure after initializing measurements.
        self.compute_initial_figure()

        # Initialize attributes for zoom box coordinates.
        self.zoom_mode_enabled = False
        self.zoom_box_start = None
        self.zoom_box_end = None

        # Connect mouse events for dragging to zoom.
        self.mpl_connect('button_press_event', self.on_mouse_press)
        self.mpl_connect('button_release_event', self.on_mouse_release)
        self.mpl_connect('motion_notify_event', self.on_mouse_motion_canvas)
        self.mpl_connect('scroll_event', self.on_scroll)

        # Assuming an initial plot size.
        self.setFixedSize(1000, 800)  # Adjust as needed.
        self.selection_rect = None  # For the dynamic zoom box rectangle

    def toggle_zoom_mode_canvas(self):
        self.zoom_mode_enabled = not self.zoom_mode_enabled
        if not self.zoom_mode_enabled:
            self.cleanup_zoom_box()

    def cleanup_zoom_box(self):
        # Reset zoom box and selection rectangle if zoom mode is toggled off
        self.zoom_box_start = None
        self.zoom_box_end = None
        if self.selection_rect:
            self.selection_rect.remove()
            self.selection_rect = None
            self.draw_idle()

    def on_mouse_motion_canvas(self, event):
        if self.zoom_mode_enabled and self.zoom_box_start:
            x0, y0 = self.zoom_box_start
            self.selection_rect.set_width(abs(event.xdata - x0))
            self.selection_rect.set_height(abs(event.ydata - y0))
            self.selection_rect.set_xy((min(x0, event.xdata), min(y0, event.ydata)))
            self.draw_idle()

    def start_dragging_point(self):
        self.is_dragging = True

    def end_dragging_point(self):
        self.is_dragging = False

    def on_figure_click(self, event):
        if event.button != 1 or event.inaxes != self.axes: return
        new_point, = self.axes.plot(event.xdata, event.ydata, 'mo', markersize=5, picker=5)
        self.draggable_points.append(DraggablePoint(new_point, self, self.delete_point))

    def delete_point(self, draggable_point):
        draggable_point.point.remove()
        self.draggable_points.remove(draggable_point)
        self.draw_idle()

    def save_points(self):
        point_positions = [(point.point.get_xdata()[0], point.point.get_ydata()[0]) for point in self.draggable_points]
        with open('saved_points.txt', 'w') as f:
            for x, y in point_positions:
                f.write(f'{x}, {y}\n')
        print("Points saved to 'saved_points.txt'.")

    def reset_zoom(self):
        # Reset view limits to initial full extent
        self.axes.set_xlim(self.initial_xlim)
        self.axes.set_ylim(self.initial_ylim)
        self.draw_idle()

    def compute_initial_figure(self):
        X, Y, sg_db, dynamic_range = self.measurements.draw_spectrogram()
        self.axes.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
        self.axes.set_ylabel('Frequency [Hz]')
        self.axes.set_xlabel('Time [sec]')

        self.initial_xlim = self.axes.get_xlim()
        self.initial_ylim = self.axes.get_ylim()

        self.add_draggable_points()

    def on_mouse_press(self, event):
        # Initiate zoom only if in zoom mode and the event is within the axes
        if self.zoom_mode_enabled and event.inaxes == self.axes:
            self.zoom_box_start = (event.xdata, event.ydata)
            if not self.selection_rect:
                self.selection_rect = Rectangle(
                    (0, 0), 0, 0, facecolor='none', edgecolor='black',
                    linestyle='--', linewidth=2, fill=False
                )
                self.axes.add_patch(self.selection_rect)
            self.selection_rect.set_visible(True)  # Ensure it's visible
            self.selection_rect.set_width(0)
            self.selection_rect.set_height(0)
            self.selection_rect.set_xy((event.xdata, event.ydata))
            self.draw_idle()

    def on_mouse_release(self, event):
        # Apply zoom if in zoom mode and the selection rectangle has been started
        if self.zoom_mode_enabled and self.zoom_box_start and self.selection_rect:
            self.zoom_box_end = (event.xdata, event.ydata)
            self.perform_zoom(event.xdata, event.ydata)
            # Clean up
            self.selection_rect.set_visible(False)  # Hide the rectangle
            self.zoom_box_start = None
            self.toggle_zoom_mode_canvas()  # Optionally toggle off the zoom mode here
            self.draw_idle()

    def perform_zoom(self, x1, y1):
        if not self.zoom_box_start or not x1 or not y1:
            return
        x0, y0 = self.zoom_box_start
        xmin, xmax = sorted([x0, x1])
        ymin, ymax = sorted([y0, y1])
        self.axes.set_xlim([xmin, xmax])
        self.axes.set_ylim([ymin, ymax])
        self.draw_idle()

    def redraw_loess_curves(self):
        # Method to redraw LOESS curves
        while len(self.axes.lines) > 0:
            line = self.axes.lines[0]  # Get the first line
            line.remove()  # Remove it
        self.redraw_points_and_curves()

    def calculate_zoom_factor(self):
        # Example conceptual calculation:
        # Determine the current range of the x-axis
        cur_xlim = self.axes.get_xlim()
        cur_xrange = cur_xlim[1] - cur_xlim[0]
        
        # Determine a target zoom level or factor based on some condition or input
        target_zoom_level = 0.5  # This is an arbitrary value for demonstration
        
        # Calculate the zoom factor based on the current range and the target zoom level
        zoom_factor = target_zoom_level / cur_xrange  # Simplified example calculation
        
        return zoom_factor

    def redraw_points_and_curves(self):
        self.add_draggable_points()
        self.redraw_loess_curves_based_on_updated_points()

    def add_draggable_points(self):
        # Retrieve formant data
        times, f1s, f2s, f3s, f4s, non_silent_segments = self.measurements.get_formants()

        # Define colors for each formant for both points and connecting lines
        formants_data = [(f1s, 'r'), (f2s, 'b'), (f3s, 'g'), (f4s, 'y')]
        
        for formant, color in formants_data:
            previous_x = previous_y = None
            for time, freq in zip(times, formant):
                current_point, = self.axes.plot(time, freq, 'o', markersize=5, picker=5, color=color)
            draggable_point = DraggablePoint(current_point, self, self.delete_point, self.redraw_loess_curves)
            self.draggable_points.append(draggable_point)
            #self.redraw_loess_curves()
            
            #.axes.plot(times, f1s, 'o', label='Original Data')

        for start_idx, end_idx in non_silent_segments:
            times_segment = times[start_idx:end_idx+1]
            f1s_segment = f1s[start_idx:end_idx+1]
            f2s_segment = f2s[start_idx:end_idx+1]
            f3s_segment = f3s[start_idx:end_idx+1]
            f4s_segment = f4s[start_idx:end_idx+1]

            smoothed_f1 = lowess(f1s_segment, times_segment, frac=0.33)  # Adjust frac as needed
            self.axes.plot(smoothed_f1[:, 0], smoothed_f1[:, 1], label=f'LOESS Segment {start_idx}-{end_idx}')
            
            smoothed_f2 = lowess(f2s_segment, times_segment, frac=0.33)  # Adjust frac as needed
            self.axes.plot(smoothed_f2[:, 0], smoothed_f2[:, 1], label=f'LOESS Segment {start_idx}-{end_idx}')

            smoothed_f3 = lowess(f3s_segment, times_segment, frac=0.33)  # Adjust frac as needed
            self.axes.plot(smoothed_f3[:, 0], smoothed_f3[:, 1], label=f'LOESS Segment {start_idx}-{end_idx}')

            smoothed_f4 = lowess(f4s_segment, times_segment, frac=0.33)  # Adjust frac as needed
            self.axes.plot(smoothed_f4[:, 0], smoothed_f4[:, 1], label=f'LOESS Segment {start_idx}-{end_idx}')


        self.draw_idle()  # Redraw the canvas to show the added points and lines

    def on_scroll(self, event):
        # Implement zoom functionality
        base_scale = 1.5  # Determines the speed of zoom
        # Get the current axis limits
        cur_xlim = self.axes.get_xlim()
        cur_ylim = self.axes.get_ylim()

        cur_xrange = (cur_xlim[1] - cur_xlim[0]) * 0.5
        cur_yrange = (cur_ylim[1] - cur_ylim[0]) * 0.5
        xdata = event.xdata  # Get event x location
        ydata = event.ydata  # Get event y location

        if event.button == 'up':
            # Zoom in
            scale_factor = 1 / base_scale
        elif event.button == 'down':
            # Zoom out
            scale_factor = base_scale
        else:
            # Unhandled scroll event
            scale_factor = 1

        # After adjusting zoom, resize the canvas if needed
        zoom_factor = self.calculate_zoom_factor()  # Calculate the zoom factor
        new_width = self.original_width * zoom_factor
        new_height = self.original_height * zoom_factor
        self.setMinimumSize(new_width, new_height)  # Update the canvas size
        self.resize(new_width, new_height)  # You might need to explicitly resize the canvas
        self.updateGeometry()  # Request the layout system to recompute the geometry

        # Set new limits
        self.axes.set_xlim([xdata - cur_xrange * scale_factor,
                            xdata + cur_xrange * scale_factor])
        self.axes.set_ylim([ydata - cur_yrange * scale_factor,
                            ydata + cur_yrange * scale_factor])

        self.draw_idle()  # Redraw the canvas to update the plot

    def on_motion(self, event):
        if not self.zoom_box_start or self.is_dragging_point or not self.selection_rect:
            return
        x0, y0 = self.zoom_box_start
        dx = event.xdata - x0
        dy = event.ydata - y0
        self.selection_rect.set_width(dx)
        self.selection_rect.set_height(dy)
        self.selection_rect.set_xy((min(x0, event.xdata), min(y0, event.ydata)))
        self.draw_idle()
