#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
import vtk
import numpy as np
from tvb.datatypes.sensors import SensorsEEG
import os


def create_sphere(center, radius=0.8, color=[255 / 255, 104 / 255, 65 / 255]):
    """
    Create sphere in 3D
    :param center: center of the sphere
    :param radius: radius of the sphere
    :param color: color of the sphere
    :return: the actors of the sphere
    """
    # create the sphere
    sphereSource = vtk.vtkSphereSource()
    sphereSource.SetCenter(center[0], center[1], center[2])
    sphereSource.SetRadius(radius)
    # Make the surface smooth.
    sphereSource.SetPhiResolution(100)
    sphereSource.SetThetaResolution(100)
    # mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())
    # actor
    actor_sphere = vtk.vtkActor()
    actor_sphere.SetMapper(mapper)
    actor_sphere.GetProperty().SetColor(color[0], color[1], color[2])
    actor_sphere.GetProperty().SetLighting(True)
    actor_sphere.GetProperty().SetDiffuse(100.0)
    return actor_sphere


def create_electrode(center, height, radius=1.0):
    """
    create a cylinder for modelling
    :param center: the center of cylinder
    :param height: the size the cylinder
    :param radius: radius of the end
    :return: actor of the cylinder
    """
    # create cone
    cone = vtk.vtkConeSource()
    cone.SetResolution(60)
    cone.SetHeight(height)
    cone.SetRadius(radius)

    # rotation of the cylinder
    transform_1 = vtk.vtkTransform()
    transform_1.RotateY(90)
    transform_2 = vtk.vtkTransform()
    transform_2.Translate(center[0], center[1], center[2] + height / 2)
    transformFilter_1 = vtk.vtkTransformPolyDataFilter()
    transformFilter_1.SetInputConnection(cone.GetOutputPort())
    transformFilter_1.SetTransform(transform_1)
    transformFilter_1.Update()
    transformFilter_2 = vtk.vtkTransformPolyDataFilter()
    transformFilter_2.SetInputConnection(transformFilter_1.GetOutputPort())
    transformFilter_2.SetTransform(transform_2)
    transformFilter_2.Update()
    coneMapper = vtk.vtkPolyDataMapper()
    coneMapper.SetInputConnection(transformFilter_2.GetOutputPort())

    # actor
    coneActor = vtk.vtkActor()
    coneActor.SetMapper(coneMapper)

    return coneActor


def create_electrode_ECOG(center, angleY=0, angleX=0, radius_ext=1.0, radius_in=2.0):
    """
    create a cylinder for modelling
    :param center: the center of cylinder
    :param angleY: angle of Y rotation
    :param angleX: angle of X rotation
    :param radius_in: radius of internal circle of the disk
    :param radius_ext: radius of external circle of the disk
    :return: actor of the cylinder
    """
    # create cone
    disk = vtk.vtkDiskSource()
    disk.SetInnerRadius(radius_in)
    disk.SetOuterRadius(radius_ext)
    disk.SetRadialResolution(100)
    disk.SetCircumferentialResolution(100)
    disk.Update()

    # transformation of the disk
    transform = vtk.vtkTransform()
    transform.RotateY(angleY)
    transform.RotateX(angleX)
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputConnection(disk.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()

    # rotation of cylinder
    transform_2 = vtk.vtkTransform()
    transform_2.Translate(center[0], center[1], center[2])
    transformFilter_2 = vtk.vtkTransformPolyDataFilter()
    transformFilter_2.SetInputConnection(transformFilter.GetOutputPort())
    transformFilter_2.SetTransform(transform_2)
    transformFilter_2.Update()

    coneMapper = vtk.vtkPolyDataMapper()
    coneMapper.SetInputConnection(transformFilter_2.GetOutputPort())

    # actor
    coneActor = vtk.vtkActor()
    coneActor.SetMapper(coneMapper)

    return coneActor


def create_Image(path, center, scale, shift_x, shift_y, shit_z):
    """

    :param path: path for the mesh
    :param center: centers of the regions
    :param scale: scale of the mesh
    :param shift_x: shift in x
    :param shift_y: shift in y
    :param shit_z: shift in z
    :return: the actor of the mesh
    """
    # Read the source file.
    reader = vtk.vtkPNGReader()
    reader.SetFileName(path)
    reader.Update()

    # rescale = vtk.vtkImageResize()
    # rescale.SetInputConnection(reader.GetOutputPort())
    # rescale.SetOutputDimensions(10,10,0)
    # rescale.SetResizeMethodToOutputDimensions()
    # rescale.SetOutputSpacing(10,10,0)
    # rescale.SetResizeMethodToOutputSpacing()
    # rescale.SetMagnificationFactors(0.1,0.1,0.1)
    # rescale.SetResizeMethodToMagnificationFactors()

    rescale = vtk.vtkImageChangeInformation()
    rescale.SetInputConnection(reader.GetOutputPort())
    # rescale.SetCenterImage(1)
    rescale.SetSpacingScale(scale, scale, scale)
    rescale.SetOriginTranslation(center[0] + shift_x, center[1] + shift_y, center[2] + shit_z)

    # transformation of the render
    transform = vtk.vtkTransform()
    transform.RotateZ(0)
    transform.Translate([0, 0, 0])
    transformFilter = vtk.vtkImageReslice()
    transformFilter.SetInputConnection(reader.GetOutputPort())
    transformFilter.SetResliceTransform(transform)
    transformFilter.Update()

    # Display the image
    actor = vtk.vtkImageActor()
    actor.GetMapper().SetInputConnection(rescale.GetOutputPort())
    # actor.GetMapper().SetInputConnection(reader.GetOutputPort())
    return actor


class MyInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """
    class for the interaction for getting the position of the camera on the left click
    """

    def __init__(self, camera, parent=None):
        """
        initialise
        :param camera: the camera state
        :param parent: of the initial object
        """
        self.AddObserver("MiddleButtonPressEvent", self.middleButtonPressEvent)
        self.AddObserver("MiddleButtonReleaseEvent", self.middleButtonReleaseEvent)
        self.AddObserver('LeftButtonPressEvent', self.middleButtonPressEventLeft, 1.0)
        self.AddObserver('LeftButtonReleaseEvent', self.middleButtonReleaseEventLeft, 1.0)
        self.camera = camera

    def middleButtonPressEvent(self, obj, event):
        """
        event example
        :param obj:
        :param event:
        :return:
        """
        print("Middle Button pressed")
        self.OnMiddleButtonDown()
        return

    def middleButtonReleaseEvent(self, obj, event):
        """
        test example
        :param obj:
        :param event:
        :return:
        """
        print("Middle Button released")
        self.OnMiddleButtonUp()
        return

    def middleButtonPressEventLeft(self, obj, event):
        """
        left click for get the position of the camera
        :param obj:
        :param event:
        :return:
        """
        print("Left Button press")
        print("position : ", self.camera.GetPosition())
        print("focal point : ", self.camera.GetFocalPoint())
        print("view up : ", self.camera.GetViewUp())
        print("distance : ", self.camera.GetDistance())
        self.OnLeftButtonDown()
        return

    def middleButtonReleaseEventLeft(self, obj, event):
        """
        Left click for fun
        :param obj:
        :param event:
        :return:
        """
        print("Left Button released")
        self.OnLeftButtonUp()
        return


def print_mouse(path, file_3d, file_center, color_TVB, color_Nest, Nest_node, electrode=None, electrode_ECOG=None,
                save_path=None, logo=None, transparency=0.3, figsize=(1000, 1000)):
    """
    plot the 3d plot of te mouse
    :param path: path of the data
    :param file_3d: file of 3d of the mouse brain
    :param file_center: file of the center of regions
    :param color_TVB: color of TVB node
    :param color_Nest: color of Nest node
    :param Nest_node: the node simulate in Nest
    :param electrode: the file of the position of the electrode
    :param electrode_ECOG: file with ECOG electrodes
    :param save_path: the path of save png
    :param logo: if the node are represent by the logo
    :param transparency: transparency of teh mesh
    :return: nothing
    """
    # get the 3d shape of mouse brain
    reader = vtk.vtkSTLReader()
    reader.SetFileName(path + file_3d)
    reader.Update()
    # transformation of the render
    transform = vtk.vtkTransform()
    transform.RotateZ(180)
    transform.Scale(10, 10, 10)
    transform.Translate([-5.5, -5.2, 3.0])
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputConnection(reader.GetOutputPort())
    transformFilter.SetTransform(transform)
    transformFilter.Update()
    # mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(transformFilter.GetOutputPort())
    # actor of mouse
    actor_mouse = vtk.vtkActor()
    actor_mouse.SetMapper(mapper)
    actor_mouse.GetProperty().SetOpacity(transparency)
    actor_mouse.GetProperty().SetColor(1, 1, 1)

    # Create a sphere by region
    actors_regions = []
    position = np.loadtxt(path + file_center)
    for i in range(position.shape[1]):
        if i not in Nest_node:
            # region simulate in TVB
            if logo is None:
                actors_regions.append(
                    create_sphere([position[0, i], position[1, i], position[2, i]], radius=color_TVB[-1],
                                  color=color_TVB))
            else:
                actors_regions.append(
                    create_Image(os.path.abspath(logo[1]), [position[0, i], position[1, i], position[2, i]], 0.01, -4,
                                 0.0, 2.5))
        else:
            if logo is None:
                # region simulate with Nest
                theta_1 = np.random.rand(1000) * 2 * np.pi
                theta_2 = np.random.rand(1000) * 2 * np.pi
                r = np.random.rand(1000) * 1.5
                xp = position[0, i] + r * np.cos(theta_1)
                yp = position[1, i] + r * np.sin(theta_1) / 2 + r * np.sin(theta_2) / 2
                zp = position[2, i] + r * np.cos(theta_2)
                centers = np.squeeze(np.swapaxes(np.concatenate([[xp], [yp], [zp]], axis=0), 0, 1))
                for center in centers:
                    actors_regions.append(create_sphere(center, radius=color_Nest[-1], color=color_Nest))
            else:
                actors_regions.append(
                    create_Image(os.path.abspath(logo[0]), [position[0, i], position[1, i], position[2, i]], 0.03, -3,
                                 0.0, 1.5))

    # create electrode if there file
    coneActor = []
    if electrode is not None:
        file = open(os.path.abspath(path + electrode), 'r')
        for index, x in enumerate(file):
            position = [float(i) for i in x.split()]
            print(index, position)
            electrode = create_electrode(position, 30)
            electrode.GetProperty().SetColor(0, 1, 0)
            coneActor.append(electrode)

    # create electrode if there file
    diskActor = []
    if electrode_ECOG is not None:
        sensor = SensorsEEG().from_file(os.path.abspath(path + electrode_ECOG))
        positions = sensor.locations
        anglesY = [-10, -38, -20, -20, -30, -30, -10, -10]
        anglesX = [0, 0, 0, -15, 5, -5, 5, -10]
        for i in range(8):
            disk = create_electrode_ECOG(positions[i], angleX=anglesX[i], angleY=anglesY[i])
            disk.GetProperty().SetColor(191 / 255, 191 / 255, 0 / 255)
            diskActor.append(disk)
        anglesY = [45, 15, 25, 20, 15, 25, 35, 35]
        anglesX = [0, 0, 8, -5, 7, -5, 5, -5]
        for i in range(8):
            disk = create_electrode_ECOG(positions[i + 8], angleX=anglesX[i], angleY=anglesY[i])
            disk.GetProperty().SetColor(0.5, 0.5, 1.0)
            diskActor.append(disk)

    # Create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    ren.SetBackground([1, 1, 1])
    renWin.SetSize(figsize[0], figsize[1])

    # Create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Assign actor to the renderer
    ren.AddActor(actor_mouse)
    for actor in actors_regions:
        actor.GetProperty().SetOpacity(1.0)
        ren.AddActor(actor)
    for actor in coneActor:
        ren.AddActor(actor)
    for actor in diskActor:
        ren.AddActor(actor)

    # define the camera
    camera = vtk.vtkCamera()

    # TOP
    # camera.SetPosition(110,130, 320)
    # camera.SetFocalPoint(55, 65, 0)

    # side
    # camera.SetPosition(90.0,-16.0,320.0)
    # camera.SetFocalPoint(50.0,64.0,0.3)
    # camera.SetViewUp(-0.65,0.70,0.25)

    # iso
    camera.SetPosition(160.0, -63.0, 300.0)
    camera.SetFocalPoint(40.0, 70.0, 20.0)
    camera.SetViewUp(-0.50, 0.65, 0.55)

    # add the camera
    ren.SetActiveCamera(camera)
    iren.SetInteractorStyle(MyInteractorStyle(camera))

    # screenshot code:
    renWin.Render()
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()

    # save if there are a file
    if save_path is None:
        # Enable user interface interactor
        iren.Initialize()
        iren.Start()
        renWin.Finalize()
        iren.TerminateApp()
        del renWin, iren
    else:
        writer = vtk.vtkPNGWriter()
        writer.SetFileName(save_path)
        writer.SetInputData(w2if.GetOutput())
        writer.Write()
        renWin.Finalize()
        del renWin


if __name__ == '__main__':
    import os
    path_global = os.path.dirname(os.path.realpath(__file__))
    # mouse brain
    print_mouse(path_global + '/../parameter/data_mouse/', 'mouse_brain.stl', 'centres.txt',
                [71 / 255, 164 / 255, 226 / 255, 1.0], [255 / 255, 104 / 255, 65 / 255, 0.5], Nest_node=[26, 78],
                # save_path=path_global + '/../data/figure//mouse_3d.png'
                )

    # mouse brain with logo
    print_mouse(path_global + '/../parameter/data_mouse/', 'mouse_brain.stl', 'centres.txt',
                [71 / 255, 164 / 255, 226 / 255, 1.0], [255 / 255, 104 / 255, 65 / 255, 0.5], Nest_node=[26, 78],
                logo=['./logo_Nest.png', './logo_TVB.png'],
                transparency=0.3,
                # save_path=path_global + '/../data/figure/mouse_3d_logo.png'
                )

    # mouse brian with electrode
    print_mouse(path_global + '/../parameter/data_mouse/', 'mouse_brain.stl', 'centres.txt',
                [71 / 255, 164 / 255, 226 / 255, 1.0], [255 / 255, 104 / 255, 65 / 255, 0.5],
                Nest_node=[26, 78],
                electrode='electrode_hypocampus.txt', electrode_ECOG='sensor_hypocampus.txt',
                transparency=0.2,  # or 1.0
                save_path=path_global + '/../data/figure/mouse_elect.png'
                )

    # mouse brian for the overview
    print_mouse(path_global + '/../parameter/data_mouse/', 'mouse_brain.stl', 'centres.txt',
                [71 / 255, 164 / 255, 226 / 255, 1.0], [255 / 255, 104 / 255, 65 / 255, 0.5],
                Nest_node=[26, 78],
                transparency=0.2,  # or 1.0
                save_path=path_global + '/../data/figure/mouse_overview.png'
                )
