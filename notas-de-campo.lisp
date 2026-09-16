(defpackage #:rimefall
  (:use #:cl)
  (:export #:iniciar-jogo #:iniciar-guerra #:executar-testes))
(in-package #:rimefall)

;;; O catálogo é imutável. O acervo guarda evidências, nunca equipamento físico.
(defstruct (conhecimento (:constructor criar-conhecimento)
                        (:predicate conhecimento-p) (:copier copiar-conhecimento))
  identificador titulo descricao criterio categoria)
(defstruct (evidencia (:constructor criar-evidencia)
                     (:predicate evidencia-p) (:copier copiar-evidencia))
  conhecimento soldado instante descricao)
(defstruct (notas (:constructor criar-notas) (:predicate notas-p) (:copier copiar-notas))
  (arma :fuzil) preparo (texto ""))

(defparameter *catalogo*
  (list
   (criar-conhecimento :identificador :fuzil :titulo "Fuzil de ferrolho"
    :descricao "Quatro cartuchos na arma. Oito de reserva."
    :criterio "Treinamento básico do esquadrão." :categoria :arma)
   (criar-conhecimento :identificador :escopeta :titulo "Escopeta de patrulha"
    :descricao "Dois cartuchos na arma. Seis de reserva."
    :criterio "Eliminar uma criatura com a escopeta." :categoria :arma)
   (criar-conhecimento :identificador :carabina :titulo "Carabina semiautomática"
    :descricao "Oito cartuchos. Dezesseis de reserva. Dois tiros de perto."
    :criterio "Encontrar a carabina no setor norte e eliminar uma criatura." :categoria :arma)
   (criar-conhecimento :identificador :submetralhadora :titulo "Submetralhadora"
    :descricao "Vinte cartuchos. Vinte de reserva. Rajadas curtas."
    :criterio "Eliminar uma criatura com a submetralhadora encontrada." :categoria :arma)
   (criar-conhecimento :identificador :precisao :titulo "Fuzil de precisão"
    :descricao "Luneta 2x. Dez cartuchos e dez de reserva. Semiautomático."
    :criterio "Eliminar uma criatura com o fuzil de precisão encontrado." :categoria :arma)
   (criar-conhecimento :identificador :franco-atirador :titulo "Fuzil de franco-atirador"
    :descricao "Luneta 4x. Cinco cartuchos e cinco de reserva. Ferrolho lento."
    :criterio "Eliminar uma criatura com o fuzil de franco-atirador." :categoria :arma)
   (criar-conhecimento :identificador :silencio :titulo "Disciplina de silêncio"
    :descricao "Revestimento: metade do alcance sonoro dos passos."
    :criterio "Atrair uma criatura e ficar em silêncio até a busca terminar."
    :categoria :preparo)
   (criar-conhecimento :identificador :distracao :titulo "Distração sonora"
    :descricao "Bolsa de iscas: quatro unidades em vez de duas."
    :criterio "Desviar com uma isca uma criatura que investiga seus ruídos."
    :categoria :preparo)
   (criar-conhecimento :identificador :temporizador :titulo "Isca temporizada"
    :descricao "Dispositivo recuperável: atraso de 3 s, ruído por 5 s."
    :criterio "Desviar a investigação de um ruído seu com o dispositivo." :categoria :preparo)
   (criar-conhecimento :identificador :bipé :titulo "Bipé portátil"
    :descricao "Apoio no chão ao agachar. Reduz a oscilação da mira."
    :criterio "Eliminar uma criatura usando o apoio do bipé." :categoria :preparo)))

(defun procurar-conhecimento (identificador)
  (find identificador *catalogo* :key #'conhecimento-identificador))

(defun criar-acervo ()
  (let ((acervo (make-hash-table)))
    (setf (gethash :fuzil acervo)
          (list (criar-evidencia :conhecimento :fuzil :soldado 0 :instante 0.0
                                :descricao "Treinamento básico do esquadrão.")))
    acervo))

(defun validar-notas (notas acervo)
  "Retorna uma explicação em português quando o preparo é inválido."
  (cond
    ((not (member (notas-arma notas) '(:fuzil :escopeta :carabina :submetralhadora :precisao :franco-atirador))) "Selecione uma arma válida.")
    ((not (gethash (notas-arma notas) acervo)) "Essa arma ainda não foi aprendida.")
    ((not (member (notas-preparo notas) '(nil :silencio :distracao :temporizador :bipé)))
     "Selecione apenas um preparo tático válido.")
    ((and (notas-preparo notas) (not (gethash (notas-preparo notas) acervo)))
     "Esse preparo ainda não foi aprendido.")
    (t nil)))

(defun incorporar-evidencias (acervo evidencias)
  "Conserva a origem sem repetir a mesma descoberta da mesma vida."
  (dolist (evidencia evidencias)
    (let* ((chave (evidencia-conhecimento evidencia))
           (anteriores (gethash chave acervo)))
      (unless (find (evidencia-soldado evidencia) anteriores :key #'evidencia-soldado)
        (setf (gethash chave acervo) (append anteriores (list evidencia))))))
  acervo)
