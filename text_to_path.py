"""
Convert text to a list of (x, y) waypoints for the robot to draw.
Output: list of strokes, each stroke is a list of (x, y) points in mm.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

def text_to_waypoints(text, height_mm=30, origin=(0, 0)):
    """
    Convert text into a list of strokes.
    Each stroke is a list of (x_mm, y_mm) points.
    Pen-up between strokes, pen-down during a stroke.
    """
    fp = FontProperties(family='sans-serif', size=height_mm)
    path = TextPath((0, 0), text, prop=fp)
    
    strokes = []
    current_stroke = []
    
    for verts, code in path.iter_segments():
        if code == 1:  # MOVETO — start a new stroke
            if current_stroke:
                strokes.append(current_stroke)
            current_stroke = [(verts[0] + origin[0], verts[1] + origin[1])]
        elif code == 2:  # LINETO — continue stroke
            current_stroke.append((verts[0] + origin[0], verts[1] + origin[1]))
        elif code == 3:  # CURVE3 — quadratic bezier, sample it
            x0, y0 = current_stroke[-1]
            x1, y1, x2, y2 = verts
            for t in np.linspace(0, 1, 10):
                bx = (1-t)**2*x0 + 2*(1-t)*t*x1 + t*t*x2
                by = (1-t)**2*y0 + 2*(1-t)*t*y1 + t*t*y2
                current_stroke.append((bx + origin[0], by + origin[1]))
        elif code == 4:  # CURVE4 — cubic bezier
            x0, y0 = current_stroke[-1]
            x1, y1, x2, y2, x3, y3 = verts
            for t in np.linspace(0, 1, 15):
                bx = (1-t)**3*x0 + 3*(1-t)**2*t*x1 + 3*(1-t)*t*t*x2 + t**3*x3
                by = (1-t)**3*y0 + 3*(1-t)**2*t*y1 + 3*(1-t)*t*t*y2 + t**3*y3
                current_stroke.append((bx + origin[0], by + origin[1]))
        elif code == 79:  # CLOSEPOLY — close stroke
            if current_stroke:
                current_stroke.append(current_stroke[0])
    
    if current_stroke:
        strokes.append(current_stroke)
    
    return strokes


def strokes_to_3d(strokes, z_draw=0.0, z_lift=5.0):
    """
    Flatten strokes into a single list of (x, y, z) waypoints.
      z == z_draw  → pen on paper, draw
      z == z_lift  → pen lifted, travel between strokes
    Sequence per stroke: approach (z_lift) → lower (z_draw) → draw → lift (z_lift).
    """
    waypoints = []
    for stroke in strokes:
        x0, y0 = stroke[0]
        waypoints.append((x0, y0, z_lift))   # move to start with pen up
        waypoints.append((x0, y0, z_draw))   # lower pen
        for x, y in stroke[1:]:
            waypoints.append((x, y, z_draw))
        xN, yN = stroke[-1]
        waypoints.append((xN, yN, z_lift))   # lift pen after stroke
    return waypoints


def visualize(strokes, title="Path"):
    """Plot strokes to verify."""
    fig, ax = plt.subplots(figsize=(8, 4))
    for stroke in strokes:
        xs = [p[0] for p in stroke]
        ys = [p[1] for p in stroke]
        ax.plot(xs, ys, 'b-', linewidth=1)
        ax.plot(xs[0], ys[0], 'go', markersize=5)  # start
        ax.plot(xs[-1], ys[-1], 'rx', markersize=5)  # end
    ax.set_aspect('equal')
    ax.set_title(f"{title} ({len(strokes)} strokes)")
    ax.grid(True, alpha=0.3)
    plt.xlabel("x (mm)")
    plt.ylabel("y (mm)")
    plt.show()


if __name__ == "__main__":
    word = "hello"
    strokes = text_to_waypoints(word, height_mm=30, origin=(0, 0))
    
    print(f"'{word}' = {len(strokes)} strokes")
    total_points = sum(len(s) for s in strokes)
    print(f"Total waypoints: {total_points}")
    
    # show first few points of each stroke
    for i, s in enumerate(strokes[:3]):
        print(f"  Stroke {i}: {len(s)} pts, starts at ({s[0][0]:.1f}, {s[0][1]:.1f})")
    
    visualize(strokes, word)