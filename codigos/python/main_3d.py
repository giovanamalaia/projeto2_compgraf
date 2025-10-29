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

# === Variáveis globais ===
g_animation_engines = []
shd_sun = shd_mercury = shd_space = shd_earth = shd_moon = None
light = None
scene_skybox = None
scene = None

# Câmeras
viewer_pos = glm.vec3(0.0, 10.0, 15.0)
active_camera = 0  # 0 = global, 1 = Terra-Lua
camera_global = None
camera_earth_moon = None
earth_moon_cam_engine = None

# === Engines de animação ===
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

class EarthMoonCameraEngine:
    def __init__(self, camera, earth_transform, moon_transform):
        self.camera = camera
        self.earth_transform = earth_transform
        self.moon_transform = moon_transform

    def update(self):
        # obtém posição da Terra e da Lua
        earth_mat = self.earth_transform.GetMatrix()
        moon_mat = self.moon_transform.GetMatrix()
        earth_pos = glm.vec3(earth_mat[3][0], earth_mat[3][1], earth_mat[3][2])
        moon_pos = glm.vec3(moon_mat[3][0], moon_mat[3][1], moon_mat[3][2])

        # vetor da Terra para a Lua
        direction = glm.normalize(moon_pos - earth_pos)

        # posiciona a câmera um pouco atrás da Terra, olhando para a Lua
        camera_pos = earth_pos - direction * 3.0 + glm.vec3(0.0, 1.0, 0.0)  # elevação opcional
        self.camera.SetPosition(camera_pos.x, camera_pos.y, camera_pos.z)
        self.camera.LookAt(moon_pos)



def update_scene():
    for engine in g_animation_engines:
        engine.update()
    if active_camera == 1 and earth_moon_cam_engine is not None:
        earth_moon_cam_engine.update()

def display(win):
    global scene_skybox, scene, camera_global, camera_earth_moon, active_camera
    global shd_sun, shd_mercury, shd_space, shd_earth, shd_moon, light, viewer_pos

    # seleciona a câmera ativa
    current_camera = camera_global if active_camera == 0 else camera_earth_moon

    # atualizar uniforms dependentes da câmera e da luz
    light_pos = glm.vec3(0.0, 0.0, 0.0)

    # usamos viewer_pos ou o próprio vetor interno da câmera
    # se a câmera ativa for Terra-Lua, ela já atualiza sua posição via engine
    if active_camera == 0:
        view_pos = viewer_pos
    else:
        # para a Terra-Lua, usamos GetViewVector() ou vetor interno
        # supondo que Camera3D tenha atributo interno self.pos ou método SetPosition usado na engine
        view_pos = current_camera.GetPosition() if hasattr(current_camera, 'GetPosition') else viewer_pos


    for sh in (shd_sun, shd_mercury, shd_space, shd_earth, shd_moon):
        if sh is None:
            continue
        sh.UseProgram()
        sh.SetUniform("uLightPos", light_pos)
        sh.SetUniform("uViewPos", view_pos)

    # renderização do skybox
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDepthMask(GL_FALSE)
    glDisable(GL_CULL_FACE)
    if scene_skybox is not None:
        scene_skybox.Render(current_camera)
    glEnable(GL_CULL_FACE)
    glDepthMask(GL_TRUE)
    glClear(GL_DEPTH_BUFFER_BIT)

    # renderização da cena principal
    if scene is not None:
        scene.Render(current_camera)

# === Callback de teclado ===
def keyboard(win, key, scancode, action, mods):
    global active_camera
    if key == glfw.KEY_Q and action == glfw.PRESS:
        glfw.set_window_should_close(win, glfw.TRUE)
    if key == glfw.KEY_C and action == glfw.PRESS:
        active_camera = 1 - active_camera  # alterna câmeras

# === Inicialização da cena ===
def initialize(win):
    global camera_global, camera_earth_moon, shd_sun, shd_mercury, shd_space, shd_earth, shd_moon, light
    global earth_moon_cam_engine, scene_skybox, scene

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    # câmeras
    camera_global = Camera3D(viewer_pos.x, viewer_pos.y, viewer_pos.z)
    camera_earth_moon = Camera3D(viewer_pos.x, viewer_pos.y, viewer_pos.z)  # inicial, será atualizado pela engine

    # luz global
    light = Light(0.0, 0.0, 0.0, 1.0, "world")

    # materiais
    white = Material(1.0, 1.0, 1.0)
    white.SetShininess(10.0)
    sun_material = Material(3.0, 3.0, 3.0)
    sun_material.SetShininess(50.0)
    space_material = Material(1.0, 1.0, 1.0)
    space_material.SetShininess(1.0)

    # shaders
    def make_shader():
        shd = Shader(light, "world")
        shd.AttachVertexShader("codigos/python/shaders/ilum_vert/vertex_texture.glsl")
        shd.AttachFragmentShader("codigos/python/shaders/ilum_vert/fragment_texture.glsl")
        shd.Link()
        return shd

    # def make_bump_shader():
    #     shd = Shader(light, "world")
    #     shd.AttachVertexShader("codigos/python/shaders/ilum_vert/vertex_bump.glsl")
    #     shd.AttachFragmentShader("codigos/python/shaders/ilum_vert/fragment_bump.glsl")
    #     shd.Link()
    #     return shd

    shd_sun = make_shader()
    shd_earth = make_shader()
    shd_moon = make_shader()
    shd_mercury = make_shader()
    shd_space = make_shader()
    # shd_earth = make_bump_shader()
    # shd_moon = make_bump_shader()
    
    # texturas
    try:
        sun_tex = Texture("uTexture", "codigos/python/images/sun.jpg")
        mercury_tex = Texture("uTexture", "codigos/python/images/mercury.jpg")
        space_tex = Texture("uTexture", "codigos/python/images/space.jpg")
        earth_tex = Texture("uTexture", "codigos/python/images/earth2.jpg")
        # earth_normal = Texture("uNormalMap", "codigos/python/images/earth_normal.jpg")
        moon_tex = Texture("uTexture", "codigos/python/images/moon.jpg")
        # moon_normal = Texture("uNormalMap", "codigos/python/images/moon_normal.jpg")
    except Exception as e:
        print(f"Erro ao carregar texturas: {e}")
        glfw.terminate()
        sys.exit()

    # animações
    global g_animation_engines
    g_animation_engines.clear()

    # Sol
    trf_sun = Transform()
    g_animation_engines.append(SpinEngine3D(trf_sun, 0.1, glm.vec3(1.5, 1.5, 1.5), glm.vec3(0, 1, 0.1)))

    # Mercúrio
    trf_mercury_orbit = Transform(); g_animation_engines.append(OrbitEngine3D(trf_mercury_orbit, 0.8))
    trf_mercury_translate = Transform(); trf_mercury_translate.Translate(2.5, 0, 0)
    trf_mercury_spin = Transform(); g_animation_engines.append(SpinEngine3D(trf_mercury_spin, 0.2, glm.vec3(0.4,0.4,0.4)))

    # Terra
    trf_earth_orbit = Transform(); g_animation_engines.append(OrbitEngine3D(trf_earth_orbit, 0.3))
    trf_earth_translate = Transform(); trf_earth_translate.Translate(5.0, 0, 0)
    trf_earth_spin = Transform(); g_animation_engines.append(SpinEngine3D(trf_earth_spin, 0.2, glm.vec3(0.6,0.6,0.6), glm.vec3(0,1,0.1)))

    # Lua
    trf_moon_orbit = Transform(); g_animation_engines.append(OrbitEngine3D(trf_moon_orbit, -1.2))
    trf_moon_translate = Transform(); trf_moon_translate.Translate(1.5, 0, 0)
    trf_moon_spin = Transform(); g_animation_engines.append(SpinEngine3D(trf_moon_spin, 0.0, glm.vec3(0.3,0.3,0.3)))

    # Skybox
    trf_space = Transform(); trf_space.Scale(100.0, 100.0, 100.0)
    scene_skybox = Scene(Node(shd_space, trf_space, [space_material, space_tex], [Sphere()]))

    # inicializa shaders com uHasNormalMap
    # for sh, val in [(shd_sun, False), (shd_mercury, False), (shd_space, False), (shd_earth, True), (shd_moon, True)]:
    #     sh.UseProgram()
    #     sh.SetUniformBool("uHasNormalMap", val)

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
                                           ]
                                           )
                                  ]
                                  ),
                             Node(None, trf_earth_orbit, 
                                  nodes=[
                                      Node(None, trf_earth_translate, 
                                           nodes=[
                                               Node(shd_earth, trf_earth_spin, [white, earth_tex], [sphere]), 

                                               Node(None, trf_moon_orbit, 
                                                    nodes=[
                                                        Node(None, trf_moon_translate, 
                                                             nodes=[
                                                                 Node(shd_moon, trf_moon_spin, [white, moon_tex], [sphere]) 
                                                             ]
                                                             )
                                                    ]
                                                    )
                                           ]
                                           )
                                  ]
                                  )
                         ]
                         )
                ]
                )
    scene = Scene(root)

    # engine da câmera Terra-Lua
    earth_moon_cam_engine = EarthMoonCameraEngine(camera_earth_moon, trf_earth_translate, trf_moon_translate)

# === Função main ===
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

    print("OpenGL version: ", glGetString(GL_VERSION).decode())

    initialize(win)

    while not glfw.window_should_close(win):
        glfw.poll_events()
        update_scene()
        display(win)
        glfw.swap_buffers(win)

    glfw.terminate()

if __name__ == "__main__":
    main()
