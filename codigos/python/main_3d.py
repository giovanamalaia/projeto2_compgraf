
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

viewer_pos = glm.vec3(0.0, 10.0, 15.0)

def initialize(win):
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)

    global camera
    camera = Camera3D(viewer_pos[0], viewer_pos[1], viewer_pos[2])

    arcball = camera.CreateArcball()
    arcball.Attach(win)

    light = Light(0.0, 0.0, 0.0, 1.0, "world")

    white = Material(1.0, 1.0, 1.0)
    white.SetShininess(10.0)
    
    sun_material = Material(3.0, 3.0, 3.0)
    sun_material.SetShininess(50.0)

    space_material = Material(1.0, 1.0, 1.0) 
    space_material.SetShininess(1.0)

    def make_shader():
        shd = Shader(light, "world")
        shd.AttachVertexShader("codigos/python/shaders/ilum_vert/vertex_texture.glsl")
        shd.AttachFragmentShader("codigos/python/shaders/ilum_vert/fragment_texture.glsl")
        shd.Link()
        return shd

    shd_sun = make_shader()
    shd_earth = make_shader()
    shd_moon = make_shader()
    shd_mercury = make_shader()
    shd_space = make_shader()

    sphere = Sphere()

    try:
        sun_tex = Texture("uTexture", "codigos/python/images/sun.jpg")
        earth_tex = Texture("uTexture", "codigos/python/images/earth2.jpg")
        moon_tex = Texture("uTexture", "codigos/python/images/moon.jpg")
        mercury_tex = Texture("uTexture", "codigos/python/images/mercury.jpg")
        space_tex = Texture("uTexture", "codigos/python/images/space.jpg")
    except Exception as e:
        print(f"Erro ao carregar texturas: {e}")
        glfw.terminate()
        sys.exit()

    global g_animation_engines
    g_animation_engines.clear()

    trf_sun = Transform() 

    sun_spin_engine = SpinEngine3D(
        trf_sun,                  
        0.1,                     
        glm.vec3(1.5, 1.5, 1.5),  
        glm.vec3(0, 1, 0.1)     
    )
    g_animation_engines.append(sun_spin_engine)

    trf_mercury_orbit = Transform()
    mercury_orbit_engine = OrbitEngine3D(trf_mercury_orbit, 0.8)
    g_animation_engines.append(mercury_orbit_engine)

    trf_mercury_translate = Transform()
    trf_mercury_translate.Translate(2.5, 0, 0)

    trf_mercury_spin = Transform()
    mercury_spin_engine = SpinEngine3D(trf_mercury_spin, 0.2, glm.vec3(0.4, 0.4, 0.4))
    g_animation_engines.append(mercury_spin_engine)

    trf_earth_orbit = Transform()
    earth_orbit_engine = OrbitEngine3D(trf_earth_orbit, 0.3)
    g_animation_engines.append(earth_orbit_engine)

    trf_earth_translate = Transform()
    trf_earth_translate.Translate(5.0, 0, 0)

    trf_earth_spin = Transform()
    earth_spin_engine = SpinEngine3D(trf_earth_spin, 0.2, glm.vec3(0.6, 0.6, 0.6), glm.vec3(0, 1, 0.1))
    g_animation_engines.append(earth_spin_engine)

    trf_moon_orbit = Transform()
    moon_orbit_engine = OrbitEngine3D(trf_moon_orbit, -1.2)
    g_animation_engines.append(moon_orbit_engine)

    trf_moon_translate = Transform()
    trf_moon_translate.Translate(1.5, 0, 0)

    trf_moon_spin = Transform()
    moon_spin_engine = SpinEngine3D(trf_moon_spin, 0.0, glm.vec3(0.3, 0.3, 0.3))
    g_animation_engines.append(moon_spin_engine)

    trf_space = Transform()
    trf_space.Scale(100.0, 100.0, 100.0)
    skybox_root = Node(shd_space, trf_space, [space_material, space_tex], [sphere])

    global scene_skybox
    scene_skybox = Scene(skybox_root)

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

    global scene
    scene = Scene(root)


def display(win):
    global scene_skybox 
    global scene
    global camera
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glDepthMask(GL_FALSE)      
    glDisable(GL_CULL_FACE)   
    scene_skybox.Render(camera) 
    glEnable(GL_CULL_FACE)    
    glDepthMask(GL_TRUE)       
    glClear(GL_DEPTH_BUFFER_BIT) 
    
    scene.Render(camera)       

def keyboard(win, key, scancode, action, mods):
    if key == glfw.KEY_Q and action == glfw.PRESS:
        glfw.set_window_should_close(win, glfw.TRUE)


if __name__ == "__main__":
    main()
