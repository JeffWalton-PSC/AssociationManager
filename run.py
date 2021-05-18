from assoc_mgr import create_app

app = create_app()

# Main
if __name__ == "__main__":
    app.run(host="10.4.204.101")
    # app.run(host="127.0.0.1")
    # Set Debugger to True to use Flask Debugger. Reccomended to be used only when server is offline.
    # If debug is left True while server is in production, then there is potential to expose data.
