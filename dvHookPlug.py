"""
Ceci est un exercice pour presenter l'utilisation de \
    l'alebre lineaire dans un plug-ins python \
        vous pouvez a partir de ce plug-in creer une chaine de 3 joints \
            ces joints seront positionner en fonction de la position de \
                3 locators en input du node
"""

import maya.OpenMayaMPx as OpenMayaMPx
import maya.OpenMaya as OpenMaya
import math


class DvHookPlug(OpenMayaMPx.MPxNode):

    # Define node properties.
    kname = "dvHookPlug"
    kplugin_id = OpenMaya.MTypeId(0x90000005)

    # Define node attributes.
    rigMode = OpenMaya.MObject()
    targetMatrix = OpenMaya.MObject()
    hookMatrix = OpenMaya.MObject()
    parentInverseMatrix = OpenMaya.MObject()

    offsetMatrix = OpenMaya.MObject()

    # OUTPUTS
    xform = OpenMaya.MObject()

    translate = OpenMaya.MObject()
    translateX = OpenMaya.MObject()
    translateY = OpenMaya.MObject()
    translateZ = OpenMaya.MObject()

    rotate = OpenMaya.MObject()
    rotateX = OpenMaya.MObject()
    rotateY = OpenMaya.MObject()
    rotateZ = OpenMaya.MObject()

    scale = OpenMaya.MObject()
    scaleX = OpenMaya.MObject()
    scaleY = OpenMaya.MObject()
    scaleZ = OpenMaya.MObject()


    def __init__(self):
        OpenMayaMPx.MPxNode.__init__(self)


    def decompose_matrix(self, mMatrix):
        # Convertir MMatrix en MTransformMatrix
        mTrsfmMtx = OpenMaya.MTransformationMatrix(mMatrix)

        # Valeurs translation
        trans = mTrsfmMtx.translation(OpenMaya.MSpace.kWorld)

        # Valeur rotation Euler en radian
        quat = mTrsfmMtx.rotation()
        angles = quat.asEulerRotation()

        # Extraire scale.
        scale = [1.0, 1.0, 1.0]
        
        scaleDoubleArray = OpenMaya.MScriptUtil()
        scaleDoubleArray.createFromList( [0.0, 0.0, 0.0], 3 )
        scaleDoubleArrayPtr = scaleDoubleArray.asDoublePtr()
        
        mTrsfmMtx.getScale(scaleDoubleArrayPtr,OpenMaya.MSpace.kObject)
        scale[0] = OpenMaya.MScriptUtil().getDoubleArrayItem(scaleDoubleArrayPtr,0)
        scale[1] = OpenMaya.MScriptUtil().getDoubleArrayItem(scaleDoubleArrayPtr,1)
        scale[2] = OpenMaya.MScriptUtil().getDoubleArrayItem(scaleDoubleArrayPtr,2)
        
        return [trans.x, trans.y, trans.z], [angles.x, angles.y, angles.z], scale

    def compute(self, plug, data):

        # Read plugs.
        rigMode_state = data.inputValue(
                DvHookPlug.rigMode
            ).asBool()

        targetMatrix_mMatrix = data.inputValue(
                DvHookPlug.targetMatrix
            ).asMatrix()

        hookMatrix_mMatrix = data.inputValue(
                DvHookPlug.hookMatrix
            ).asMatrix()

        parentInverseMatrix_mMatrix = data.inputValue(
                DvHookPlug.parentInverseMatrix
            ).asMatrix()

        
        if rigMode_state:
            offset_handle = data.outputValue(
                DvHookPlug.offsetMatrix
            )
            offsetMatrix_mMatrix = targetMatrix_mMatrix * hookMatrix_mMatrix.inverse()
            offset_handle.setMMatrix(offsetMatrix_mMatrix)
        
        offsetMatrix_mMatrix = data.inputValue(
                DvHookPlug.offsetMatrix
            ).asMatrix()
        
        final_mMatrix = offsetMatrix_mMatrix * hookMatrix_mMatrix * parentInverseMatrix_mMatrix

        transforms = self.decompose_matrix(final_mMatrix)
        
        # OUTPUTS
        xform_handle = data.outputValue(self.xform)
        
        # Set output shoulder
        out_tr = xform_handle.child(
                DvHookPlug.translate
            )
        out_tr.set3Double(
                transforms[0][0],
                transforms[0][1],
                transforms[0][2]
            )

        out_rot = xform_handle.child(
                DvHookPlug.rotate
            )
        out_rot.set3Double(
                transforms[1][0],
                transforms[1][1],
                transforms[1][2]
            )

        out_scl = xform_handle.child(
                DvHookPlug.scale
            )
        out_scl.set3Double(
                transforms[2][0],
                transforms[2][1],
                transforms[2][2]
            )

        xform_handle.setClean()
        
        data.setClean(plug)

        return True


def creator():
    return OpenMayaMPx.asMPxPtr(DvHookPlug())


def initialize():
    nAttr = OpenMaya.MFnNumericAttribute()
    mAttr = OpenMaya.MFnMatrixAttribute()
    cAttr = OpenMaya.MFnCompoundAttribute()
    uAttr = OpenMaya.MFnUnitAttribute()

    # INPUTS
    DvHookPlug.rigMode = nAttr.create(
            "rigMode",
            "rigmode",
            OpenMaya.MFnNumericData.kBoolean,
            True
        )
    nAttr.setWritable(True)
    nAttr.setStorable(True)
    DvHookPlug.addAttribute(DvHookPlug.rigMode)

    DvHookPlug.targetMatrix = mAttr.create(
            "targetMatrix",
            "trgtmat"
        )
    mAttr.setStorable(True)
    DvHookPlug.addAttribute(DvHookPlug.targetMatrix)

    DvHookPlug.hookMatrix = mAttr.create(
            "hookMatrix",
            "hookmat"
        )
    mAttr.setStorable(False)
    DvHookPlug.addAttribute(DvHookPlug.hookMatrix)

    DvHookPlug.parentInverseMatrix = mAttr.create(
            "parentInverseMatrix",
            "pim"
        )
    mAttr.setStorable(False)
    DvHookPlug.addAttribute(DvHookPlug.parentInverseMatrix)

    DvHookPlug.offsetMatrix = mAttr.create(
            "offsetMatrix",
            "offm"
        )
    mAttr.setStorable(False)
    DvHookPlug.addAttribute(DvHookPlug.offsetMatrix)

    # OUTPUTS
    # Translate
    DvHookPlug.translateX = nAttr.create(
        "translateX",
        "tx",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvHookPlug.translateY = nAttr.create(
        "translateY",
        "ty",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvHookPlug.translateZ = nAttr.create(
        "translateZ",
        "tz",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvHookPlug.translate = nAttr.create(
        "translate",   "t",
        DvHookPlug.translateX,
        DvHookPlug.translateY,
        DvHookPlug.translateZ
    )
    nAttr.setStorable(False)

    # Rotate
    DvHookPlug.rotateX = uAttr.create(
        "rotateX",
        "rx",
        OpenMaya.MFnUnitAttribute.kAngle,
        0.0
    )
    DvHookPlug.rotateY = uAttr.create(
        "rotateY",
        "ry",
        OpenMaya.MFnUnitAttribute.kAngle,
        0.0
    )
    DvHookPlug.rotateZ = uAttr.create(
        "rotateZ",
        "rz",
        OpenMaya.MFnUnitAttribute.kAngle,
        0.0
    )
    DvHookPlug.rotate = nAttr.create(
        "rotate",   "r",
        DvHookPlug.rotateX,
        DvHookPlug.rotateY,
        DvHookPlug.rotateZ
    )
    nAttr.setStorable(False)

    # Scale
    DvHookPlug.scaleX = nAttr.create(
        "scaleX",
        "sx",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvHookPlug.scaleY = nAttr.create(
        "scaleY",
        "sy",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvHookPlug.scaleZ = nAttr.create(
        "scaleZ",
        "sz",
        OpenMaya.MFnNumericData.kDouble,
        0.0
    )
    DvHookPlug.scale = nAttr.create(
        "scale",   "s",
        DvHookPlug.scaleX,
        DvHookPlug.scaleY,
        DvHookPlug.scaleZ
    )
    nAttr.setStorable(False)

    DvHookPlug.xform = cAttr.create("xform", "xf")
    cAttr.addChild(DvHookPlug.translate)
    cAttr.addChild(DvHookPlug.rotate)
    cAttr.addChild(DvHookPlug.scale)
    DvHookPlug.addAttribute(DvHookPlug.xform)

    # Attribut affect
    DvHookPlug.attributeAffects(
            DvHookPlug.rigMode,
            DvHookPlug.xform
        )

    DvHookPlug.attributeAffects(
            DvHookPlug.targetMatrix,
            DvHookPlug.xform
        )

    DvHookPlug.attributeAffects(
            DvHookPlug.hookMatrix,
            DvHookPlug.xform
        )

    DvHookPlug.attributeAffects(
            DvHookPlug.parentInverseMatrix,
            DvHookPlug.xform
        )


def initializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj, "damsOLabo", "1.0", "Any")
    try:
        plugin.registerNode(
                DvHookPlug.kname,
                DvHookPlug.kplugin_id,
                creator,
                initialize
            )
    except:
        raise RuntimeError, "Failed to register node: '{}'".format(DvHookPlug.kname)


def uninitializePlugin(obj):
    plugin = OpenMayaMPx.MFnPlugin(obj)
    try:
        plugin.deregisterNode(DvHookPlug.kplugin_id)
    except:
        raise RuntimeError, "Failed to register node: '{}'".format(DvHookPlug.kname)
