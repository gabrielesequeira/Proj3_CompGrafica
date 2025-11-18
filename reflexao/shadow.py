import glm

def shadow_matrix(plane_normal, plane_point, light_position):
    """Gera uma matriz de projeção para sombras em um plano"""
    d = -glm.dot(plane_normal, plane_point)
    nx, ny, nz = plane_normal
    lx, ly, lz, lw = light_position  # Posição da luz homogênea
    shadow = glm.mat4(1.0)

    shadow[0][0] = d + nx * lx
    shadow[0][1] = nx * ly
    shadow[0][2] = nx * lz
    shadow[0][3] = nx * lw

    shadow[1][0] = ny * lx
    shadow[1][1] = d + ny * ly
    shadow[1][2] = ny * lz
    shadow[1][3] = ny * lw

    shadow[2][0] = nz * lx
    shadow[2][1] = nz * ly
    shadow[2][2] = d + nz * lz
    shadow[2][3] = nz * lw

    shadow[3][0] = -d * lx
    shadow[3][1] = -d * ly
    shadow[3][2] = -d * lz
    shadow[3][3] = -d * lw

    return shadow
