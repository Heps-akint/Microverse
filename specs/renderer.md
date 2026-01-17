# Renderer spec

Constraints:
- No external assets.
- Must render something real-time in a window.
- Start simple: 2.5D heightmap renderer (fast) before raymarch/voxels.

MVP rendering approach:
- Generate heightmap H[x,y]
- Render by sampling height + slope for shading
- Optional: horizon fog
