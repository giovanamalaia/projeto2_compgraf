import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import *
from PIL import Image, ImageOps
import glm
import sys
import math
from camera3d import *
from light import *
from shader import *
from material import *
from transform import *
from node import *
from scene import *
from cube import *
from sphere import *
from texture import *
from polyoffset import *
from quad import *
from cylinder import *

g_animation_engines = []
shd_sun = shd_mercury = shd_space = shd_earth = shd_moon = None
light = None
scene_skybox = None
scene = None

# Câmeras
viewer_pos = glm.vec3(0.0, 10.0, 15.0)
camera_global = None
camera_earth = None
active_camera = 0  # 0 = global, 1 = Terra

# Engines de animação 
class OrbitEngine3D:
    def __init__(self, transform_node, speed, axis=glm.vec3(0, 1, 0)):
        self.angle = 0.0
        self.speed = speed
        self.transform = transform_node
        self.axis = axis

    def update(self):
        self.angle = (self.angle + self.speed) % 360
        self.transform.LoadIdentity()
        self.transform.Rotate(self.angle, self.axis.x, self.axis.y, self.axis.z)

class SpinEngine3D:
    def __init__(self, transform_node, speed, scale_vec, axis=glm.vec3(0, 1, 0)):
        self.angle = 0.0
        self.speed = speed
        self.transform = transform_node
        self.scale = scale_vec
        self.axis = axis

    def update(self):
        self.angle = (self.angle + self.speed) % 360
        self.transform.LoadIdentity()
        self.transform.Scale(self.scale.x, self.scale.y, self.scale.z)
        self.transform.Rotate(self.angle, self.axis.x, self.axis.y, self.axis.z)


def update_scene():
    for engine in g_animation_engines:
        engine.update()


def display(win):
    global scene_skybox, scene, camera_global, camera_earth, active_camera

    current_camera = camera_global if active_camera == 0 else camera_earth

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDepthMask(GL_FALSE)
    glDisable(GL_CULL_FACE)
    if scene_skybox is not None:
        scene_skybox.Render(current_camera)
    glEnable(GL_CULL_FACE)
    glDepthMask(GL_TRUE)
    glClear(GL_DEPTH_BUFFER_BIT)

    if scene is not None:
        scene.Render(current_camera)

def keyboard(win, key, scancode, action, mods):
    global active_camera
    if key == glfw.KEY_Q and action == glfw.PRESS:
        glfw.set_window_should_close(win, glfw.TRUE)
    if key == glfw.KEY_C and action == glfw.PRESS:
        active_camera = 1 - active_camera  # alterna entre global e Terra


def initialize(win):
    global camera_global, camera_earth, light, scene_skybox, scene
    global shd_sun, shd_mercury, shd_space, shd_earth, shd_moon

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    # luz global
    light = Light(0.0, 0.0, 0.0, 1.0, "world")

    # materiais
    white = Material(1.0, 1.0, 1.0); white.SetShininess(10.0)
    sun_material = Material(3.0, 3.0, 3.0); sun_material.SetShininess(50.0)
    space_material = Material(1.0, 1.0, 1.0); space_material.SetShininess(1.0)

    # shaders
    def make_shader():
        shd = Shader(light, "world")
        shd.AttachVertexShader("codigos/python/shaders/ilum_vert/vertex_texture.glsl")
        shd.AttachFragmentShader("codigos/python/shaders/ilum_vert/fragment_texture.glsl")
        shd.Link()
        return shd

    shd_sun = make_shader()
    shd_moon = make_shader()
    shd_mercury = make_shader()
    shd_space = make_shader()

    shd_earth = Shader(light, "world")
    shd_earth.AttachVertexShader("codigos/python/shaders/ilum_vert/normal_map_vertex.glsl")
    shd_earth.AttachFragmentShader("codigos/python/shaders/ilum_vert/normal_map_fragment.glsl")
    shd_earth.Link()

    try:
        program_id = shd_earth.pid  
        glUseProgram(program_id)
        
        tex_loc = glGetUniformLocation(program_id, "uTexture")
        glUniform1i(tex_loc, 0) 
        norm_loc = glGetUniformLocation(program_id, "uNormalMap")
        glUniform1i(norm_loc, 1) 
        
        glUseProgram(0)

    except AttributeError:
        print("="*50)
        print("ATENÇÃO: Não achei 'shd_earth.program'.")
        print("Se o nome do atributo que guarda o ID do shader na sua classe 'Shader' for outro")
        print("(como _program, program_id, etc.), por favor, ajuste 'shd_earth.program' no código.")
        print("="*50)
        glfw.terminate()
        sys.exit()
    except Exception as e:
        print(f"Erro ao definir uniformes de textura: {e}")
    try:
        sun_tex = Texture("uTexture", "codigos/python/images/sun.jpg")
        mercury_tex = Texture("uTexture", "codigos/python/images/mercury.jpg")
        space_tex = Texture("uTexture", "codigos/python/images/space.jpg")
        earth_tex = Texture("uTexture", "codigos/python/images/earth2.jpg")
        earth_normal_tex = Texture("uNormalMap", "codigos/python/images/earth_normal.jpg")
        moon_tex = Texture("uTexture", "codigos/python/images/moon.jpg")
        moon_normal_tex = Texture("uNormalMap", "codigos/python/images/moon_normal.jpg")
    except Exception as e:
        print(f"Erro ao carregar texturas: {e}")
        glfw.terminate()
        sys.exit()

    # animações
    g_animation_engines.clear()
    trf_sun = Transform(); g_animation_engines.append(SpinEngine3D(trf_sun, 0.1, glm.vec3(1.5, 1.5, 1.5), glm.vec3(0, 1, 0.1)))
    trf_mercury_orbit = Transform(); g_animation_engines.append(OrbitEngine3D(trf_mercury_orbit, 0.8))
    trf_mercury_translate = Transform(); trf_mercury_translate.Translate(2.5, 0, 0)
    trf_mercury_spin = Transform(); g_animation_engines.append(SpinEngine3D(trf_mercury_spin, 0.2, glm.vec3(0.4,0.4,0.4)))
    trf_earth_orbit = Transform(); g_animation_engines.append(OrbitEngine3D(trf_earth_orbit, 0.3))
    trf_earth_translate = Transform(); trf_earth_translate.Translate(5.0, 0, 0)
    trf_earth_spin = Transform(); g_animation_engines.append(SpinEngine3D(trf_earth_spin, 0.2, glm.vec3(0.6,0.6,0.6), glm.vec3(0,1,0.1)))
    trf_moon_orbit = Transform(); g_animation_engines.append(OrbitEngine3D(trf_moon_orbit, -0.4))
    trf_moon_translate = Transform(); trf_moon_translate.Translate(1.5, 0, 0)
    trf_moon_spin = Transform(); g_animation_engines.append(SpinEngine3D(trf_moon_spin, 0.0, glm.vec3(0.3,0.3,0.3)))

    # Skybox
    trf_space = Transform(); trf_space.Scale(100.0, 100.0, 100.0)
    scene_skybox = Scene(Node(shd_space, trf_space, [space_material, space_tex], [Sphere()]))

    # construção da cena
    sphere = Sphere()
    root = Node(shd_sun,
                nodes=[
                    Node(shd_sun, trf_sun, [sun_material, sun_tex], [sphere],
                         nodes=[
                             Node(None, trf_mercury_orbit,
                                  nodes=[
                                      Node(None, trf_mercury_translate,
                                           nodes=[
                                               Node(shd_mercury, trf_mercury_spin, [white, mercury_tex], [sphere])
                                           ])
                                  ]),
                             Node(None, trf_earth_orbit,
                                  nodes=[
                                      Node(None, trf_earth_translate,
                                           nodes=[
                                               Node(shd_earth, trf_earth_spin, [white, earth_tex, earth_normal_tex], [sphere], name="Earth"),
                                               Node(None, trf_moon_orbit,
                                                    nodes=[
                                                        Node(None, trf_moon_translate,
                                                             nodes=[
                                                                 Node(shd_earth, trf_moon_spin, [white, moon_tex, moon_normal_tex], [sphere], name="Moon")
                                                             ])
                                                    ])
                                           ])
                                  ])
                         ])
                ])
    scene = Scene(root)

    # câmera global com arcball
    camera_global = Camera3D(viewer_pos.x, viewer_pos.y, viewer_pos.z)
    arcball = camera_global.CreateArcball()
    arcball.Attach(win)

    # câmera da Terra com referência ao nó da Terra
    earth_node = scene.FindNodeByName("Earth")
    camera_earth = Camera3D(0.0, 2.0, 5.0)
    camera_earth.SetReference(earth_node)

def main():
    if not glfw.init():
        return
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    win = glfw.create_window(800, 600, "Sistema Solar 3D", None, None)
    if not win:
        glfw.terminate()
        return
    glfw.set_key_callback(win, keyboard)
    glfw.make_context_current(win)

    print("OpenGL version:", glGetString(GL_VERSION).decode())

    initialize(win)

    while not glfw.window_should_close(win):
        glfw.poll_events()
        update_scene()
        display(win)
        glfw.swap_buffers(win)

    glfw.terminate()

if __name__ == "__main__":
    main()