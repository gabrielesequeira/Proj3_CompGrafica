import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import *
import glm
from camera3d import Camera3D
from light import Light
from shader import Shader
from material import Material
from transform import Transform
from node import Node
from scene import Scene
from sphere import Sphere

viewer_pos = glm.vec3(0.0, 0.0, 5.0)  # Posição inicial do observador

def main():
    # Inicializa a biblioteca GLFW
    if not glfw.init():
        return
    
    # Configuração da janela e do OpenGL
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)

    win = glfw.create_window(800, 800, "Esfera Iluminada", None, None)
    if not win:
        glfw.terminate()
        return

    glfw.set_key_callback(win, keyboard)
    glfw.make_context_current(win)

    print("OpenGL version: ", glGetString(GL_VERSION))

    initialize(win)

    # Loop principal
    while not glfw.window_should_close(win):
        display(win)
        glfw.poll_events()

    glfw.terminate()


def initialize(win):
    global camera
    global scene
    global shader_red
    global shader_white

    # Configurações da câmera e luz
    camera = Camera3D(viewer_pos[0], viewer_pos[1], viewer_pos[2])
    arcball = camera.CreateArcball()
    arcball.Attach(win)

    light = Light(0.0, 0.0, 1.0, 1.0, "camera")
    light.SetAmbient(0.2, 0.2, 0.2)
    light.SetDiffuse(0.8, 0.8, 0.8)
    light.SetSpecular(1.0, 1.0, 1.0)

    # Shader vermelho com iluminação
    shader_red = Shader(light, "camera")
    shader_red.AttachVertexShader("shaders/vertex.glsl")
    shader_red.AttachGeometryShader("shaders/geometry.glsl")
    shader_red.AttachFragmentShader("shaders/fragment_red.glsl")
    shader_red.Link()

    # Shader branco para linhas
    shader_white = Shader(light, "camera")
    shader_white.AttachVertexShader("shaders/vertex.glsl")
    shader_white.AttachGeometryShader("shaders/geometry.glsl")
    shader_white.AttachFragmentShader("shaders/fragment_white.glsl")
    shader_white.Link()

    # Transformação da esfera
    transform = Transform()
    transform.Scale(1.0, 1.0, 1.0)
    transform.Translate(0.0, 0.0, 0.0)

    # Esfera
    sphere = Sphere(nstack=30, nslice=30)

    # Nó raiz da cena
    root = Node(shader_red, nodes=[
        Node(None, transform, [], [sphere])
    ])

    # Cena global
    scene = Scene(root)

    # Configurações de renderização
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glDisable(GL_CULL_FACE)


def display(win):
    global scene
    global camera
    global shader_red
    global shader_white

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # Renderizar preenchimento com o shader vermelho
    scene.GetRoot().SetShader(shader_red)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    scene.Render(camera)

    # Renderizar linhas com o shader branco
    scene.GetRoot().SetShader(shader_white)
    glEnable(GL_POLYGON_OFFSET_LINE)
    glPolygonOffset(-1.0, -1.0)
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    scene.Render(camera)
    glDisable(GL_POLYGON_OFFSET_LINE)

    # Voltar ao modo padrão de preenchimento
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glfw.swap_buffers(win)


def keyboard(win, key, scancode, action, mods):
    if key == glfw.KEY_Q and action == glfw.PRESS:
        glfw.set_window_should_close(win, glfw.TRUE)


if __name__ == "__main__":
    main()
