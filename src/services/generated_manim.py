from manim import *

class PlatonicSolids(Scene):
    def construct(self):
        # Create the five Platonic solids
        tetrahedron = Tetrahedron()
        cube = Cube()
        octahedron = Octahedron()
        dodecahedron = Dodecahedron()
        icosahedron = Icosahedron()

        # Set initial positions
        tetrahedron.move_to(LEFT * 3)
        cube.move_to(LEFT * 1)
        octahedron.move_to(RIGHT * 1)
        dodecahedron.move_to(RIGHT * 3)
        icosahedron.move_to(RIGHT * 5)

        # Create a group of solids
        solids = VGroup(tetrahedron, cube, octahedron, dodecahedron, icosahedron)

        # Fast-paced montage of solids rotating and morphing
        self.play(FadeIn(solids))
        self.play(LaggedStart(
            *[Rotate(solid, angle=TAU, run_time=2) for solid in solids],
            lag_ratio=0.5
        ))

        # Focus on Tetrahedron
        self.play(Indicate(tetrahedron))
        self.wait(1)

        # Transition to Cube
        self.play(Transform(tetrahedron, cube))
        self.play(Indicate(cube))
        self.wait(1)

        # Transition to Octahedron
        self.play(Transform(cube, octahedron))
        self.play(Indicate(octahedron))
        self.wait(1)

        # Transition to Dodecahedron
        self.play(Transform(octahedron, dodecahedron))
        self.play(Indicate(dodecahedron))
        self.wait(1)

        # Transition to Icosahedron
        self.play(Transform(dodecahedron, icosahedron))
        self.play(Indicate(icosahedron))
        self.wait(1)

        # Show all five solids rotating side-by-side
        self.play(LaggedStart(
            *[Rotate(solid, angle=TAU, run_time=2) for solid in solids],
            lag_ratio=0.5
        ))

        # Convergence of solids to a single point
        self.play(solids.animate.move_to(ORIGIN).scale(0.5))
        self.wait(1)

        # End scene
        self.play(FadeOut(solids))