import adsk.core, adsk.fusion, adsk.cam, traceback

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        design = app.activeProduct
        rootComp = design.rootComponent
        sketches = rootComp.sketches

        # Parameters (in mm)
        convertFactor = 10          # Convert mm to cm
        a = 10.668  / convertFactor # Waveguide width [a]
        b = 4.318   / convertFactor # Waveguide height [b] (mm)
        A = 60  / convertFactor     # Horn aperture width (mm)
        B = 45  / convertFactor     # Horn aperture height (mm)
        L = 120  / convertFactor    # Total length of horn antenna (mm)
        L1 = 10 / convertFactor     # Length of the waveguide section at the base of the horn antenna (mm)
        t = 2   / convertFactor     # Horn wall thickness (mm)

        # TODO - add functions to create horn antenna based on desired parameters, e.g.: frequency, gain, etc.

        # Create sketch for waveguide section
        sectionSketch = sketches.add(rootComp.xYConstructionPlane)
        sectionRect = sectionSketch.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(-a/2, -b/2, 0), adsk.core.Point3D.create(a/2, b/2, 0))
        
        # Extrude waveguide section
        sectionProfile = sectionSketch.profiles.item(0)
        extrudes = rootComp.features.extrudeFeatures
        sectionExtrude = extrudes.addSimple(sectionProfile, adsk.core.ValueInput.createByReal(L1), adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        sectionBody = sectionExtrude.bodies.item(0)  # Get the body of the waveguide section

        # Find the opposite end face of the waveguide section
        sectionFaces = sectionBody.faces
        farthestFace = None
        maxDistance = 0
        for face in sectionFaces:
            faceOrigin = face.pointOnFace # Get the origin of the face
            distance = faceOrigin.distanceTo(adsk.core.Point3D.create(0, 0, 0))  # Distance from face origin to component origin
            if distance > maxDistance:
                maxDistance = distance
                farthestFace = face

        # Create a plane offset by L1 distance from the farthest face of the waveguide section
        offsetPlaneInput = rootComp.constructionPlanes.createInput()
        offsetPlaneInput.setByOffset(farthestFace, adsk.core.ValueInput.createByReal(L-L1))
        offsetPlane = rootComp.constructionPlanes.add(offsetPlaneInput)

        # Create sketch for aperture on the offset plane
        apertureSketch = sketches.add(offsetPlane)
        apertureRect = apertureSketch.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create(-A/2, -B/2, 0), adsk.core.Point3D.create(A/2, B/2, 0))
        
        # Loft from the farthest face of the waveguide section to the aperture
        loftFeatures = rootComp.features.loftFeatures
        loftInput = loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        loftSections = loftInput.loftSections
        loftSections.add(farthestFace)
        loftSections.add(apertureSketch.profiles.item(0))
        loft = loftFeatures.add(loftInput)

        # Get the scaled body reference
        loftBody = loft.bodies.item(0)
      
        # Delete sketches and planes
        apertureSketch.deleteMe()
        offsetPlane.deleteMe()

        # Duplicate the section body
        duplicatedBody = sectionBody.copyToComponent(rootComp)

        # Create a scale input
        inputColl = adsk.core.ObjectCollection.create()
        inputColl.add(duplicatedBody)
        
        basePt = sectionSketch.sketchPoints.item(0)
        scaleFactor = adsk.core.ValueInput.createByReal(1)
        
        scales = rootComp.features.scaleFeatures
        scaleInput = scales.createInput(inputColl, basePt, scaleFactor)
        
        # Calculate the scale factors
        xScaleFactor = (a + t*2) / a
        yScaleFactor = (b + t*2) / b
        zScaleFactor = 1  

        # Create the scale factors as ValueInput
        xScale = adsk.core.ValueInput.createByReal(xScaleFactor)
        yScale = adsk.core.ValueInput.createByReal(yScaleFactor)
        zScale = adsk.core.ValueInput.createByReal(zScaleFactor)

        scaleInput.setToNonUniform(xScale, yScale, zScale)
        scale = scales.add(scaleInput)

        # Get the scaled body reference
        scaledSectionBody = scale.bodies.item(0)

        # Find the opposite end face of the scaled section
        sectionFaces = scaledSectionBody.faces
        farthestFace = None
        maxDistance = 0
        for face in sectionFaces:
            faceOrigin = face.pointOnFace
            distance = faceOrigin.distanceTo(adsk.core.Point3D.create(0, 0, 0))  # Distance from face origin to component origin
            if distance > maxDistance:
                maxDistance = distance
                farthestFace = face

        # Create a plane offset by L1 distance from the farthest face of the waveguide section
        offsetPlaneInput = rootComp.constructionPlanes.createInput()
        offsetPlaneInput.setByOffset(farthestFace, adsk.core.ValueInput.createByReal(L-L1))
        offsetPlane = rootComp.constructionPlanes.add(offsetPlaneInput)

        # Create sketch for aperture on the offset plane
        apertureSketch = sketches.add(offsetPlane)
        apertureRect = apertureSketch.sketchCurves.sketchLines.addTwoPointRectangle(adsk.core.Point3D.create((-A-t*2)/2, (-B-t*2)/2, 0), adsk.core.Point3D.create((A+t*2)/2, (B+t*2)/2, 0))
        
        # Loft from the farthest face of the waveguide section to the aperture
        loftFeatures = rootComp.features.loftFeatures
        loftInput = loftFeatures.createInput(adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        loftSections = loftInput.loftSections
        loftSections.add(farthestFace)
        loftSections.add(apertureSketch.profiles.item(0))
        loft = loftFeatures.add(loftInput)
        
        # Get the scaled body reference
        scaledLoftBody = loft.bodies.item(0)
        
        # Combine bodies
        combineFeatures = rootComp.features.combineFeatures

        # Combine sectionBody and loftBody - this is the empty region within the antenna
        combineInput1 = combineFeatures.createInput(sectionBody, adsk.core.ObjectCollection.create())
        combineInput1.targetBody = sectionBody
        combineInput1.toolBodies.add(loftBody)
        combineInput1.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        combineFeatures.add(combineInput1)

        # Combine scaledSectionBody and scaledLoftBody - this is the solid region (walls) of the antenna
        combineInput2 = combineFeatures.createInput(scaledSectionBody, adsk.core.ObjectCollection.create())
        combineInput2.targetBody = scaledSectionBody
        combineInput2.toolBodies.add(scaledLoftBody)
        combineInput2.operation = adsk.fusion.FeatureOperations.JoinFeatureOperation
        combineFeatures.add(combineInput2)

        # Subtract sectionBody from scaledSectionBody - this is the final horn antenna
        combineInput3 = combineFeatures.createInput(sectionBody, adsk.core.ObjectCollection.create())
        combineInput3.targetBody = scaledSectionBody
        combineInput3.toolBodies.add(sectionBody)
        combineInput3.operation = adsk.fusion.FeatureOperations.CutFeatureOperation
        combineFeatures.add(combineInput3)
        
        # Delete sketches and planes
        sectionSketch.deleteMe()
        apertureSketch.deleteMe()
        offsetPlane.deleteMe()

    except Exception as e:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
