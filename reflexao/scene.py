import glm

class Scene:
  def __init__(self, root):
    self.root = root
    self.engines = []

  def GetRoot(self):
    return self.root

  def AddEngine(self, engine):
    self.engines.append(engine)

  def Update(self, dt):
    for e in self.engines:
      e.Update(dt)

  def Render(self, camera, model_matrix=glm.mat4(1.0)):
      """
      Renderiza a cena com uma matriz de modelo opcional.
      :param camera: A câmera usada para obter as matrizes View e Projection.
      :param model_matrix: Matriz de modelo opcional (ex.: matriz de reflexão).
      """
      from state import State
      st = State(camera)

      # Carregar a matriz de modelo no estado
      st.PushMatrix()
      st.MultMatrix(model_matrix)

      # Renderizar o nó raiz
      self.root.Render(st)

      # Restaurar a pilha de matrizes
      st.PopMatrix()