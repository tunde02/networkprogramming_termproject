import win32con
import win32gui

def isRealWindow(hWnd):
    '''Return True if given window is a real Windows application window.'''
    if not win32gui.IsWindowVisible(hWnd):
        return False
    if win32gui.GetParent(hWnd) != 0:
        return False
    hasNoOwner = win32gui.GetWindow(hWnd, win32con.GW_OWNER) == 0
    lExStyle = win32gui.GetWindowLong(hWnd, win32con.GWL_EXSTYLE)
    if (((lExStyle & win32con.WS_EX_TOOLWINDOW) == 0 and hasNoOwner)
      or ((lExStyle & win32con.WS_EX_APPWINDOW != 0) and not hasNoOwner)):
        if win32gui.GetWindowText(hWnd):
            return True
    return False

def getWindowSizes():
    '''
    Return a list of tuples (handler, (x, y), (width, height)) for each real window.
    '''
    def callback(hWnd, windows):
        if not isRealWindow(hWnd):
            return
        rect = win32gui.GetWindowRect(hWnd)
        windows.append((hWnd, (rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1]), win32gui.GetWindowText(hWnd)))
    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows

if __name__ == "__main__":
    for win in getWindowSizes():
        print(win)
        # print(win[1][0])
