class MyGLWidget(QOpenGLWidget):

# public
    MyGLWidget(QWidget parent) : QOpenGLWidget(parent) { }
# protected
    def initializeGL():

        # Set up the rendering context, load shaders and other resources, etc.:
        f = QOpenGLContext.currentContext().functions()
        f.glClearColor(1.0f, 1.0f, 1.0f, 1.0f)
        ...

    def resizeGL(w, h):

        # Update projection matrix and other size related settings:
        m_projection.setToIdentity()
        m_projection.perspective(45.0f, w / float(h), 0.01f, 100.0f)
        ...

    def paintGL():

        # Draw the scene:
        f = QOpenGLContext.currentContext().functions()
        f.glClear(GL_COLOR_BUFFER_BIT)
