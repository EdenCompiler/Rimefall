(in-package #:rimefall)

;;; Interface enxuta do protótipo. A apresentação 3D compartilha a mesma LWLGL.
(defun estado-setores-guerra (guerra)
  (mapcar (lambda (setor)
            (format nil "~A / ~A / ~D%%"
                    (setor-guerra-nome setor)
                    (or (setor-guerra-dono setor) "disputado")
                    (round (* 100 (abs (setor-guerra-progresso setor))))))
          (guerra-setores guerra)))

(defun painel-guerra (guerra)
  (list :tempo (guerra-tempo guerra) :fase (guerra-fase guerra)
        :setores (estado-setores-guerra guerra)
        :reforcos (mapcar (lambda (exercito)
                            (list (exercito-id exercito) (exercito-reforcos exercito)))
                          (guerra-exercitos guerra))
        :vencedor (guerra-vencedor guerra)
        :invasao (and (guerra-invasao guerra) :ativa)
        :mensagens (mensagens-recentes-guerra guerra 4)))

(defun desenhar-interface-guerra (guerra)
  "Desenha uma sobreposição textual que pode ser usada pelo renderizador de guerra."
  (retangulo 26 24 1228 672 '(.025 .043 .055 .82))
  (desenhar-texto "RIMEFALL / GUERRA DO CÍRCULO POLAR" 52 45 2.2 *destaque*)
  (desenhar-texto (format nil "~2,'0D:~2,'0D / ~A"
                          (floor (/ (guerra-tempo guerra) 60))
                          (mod (floor (guerra-tempo guerra)) 60)
                          (string-upcase (symbol-name (guerra-fase guerra))))
                 52 82 2 *gelo*)
  (desenhar-texto "FRENTE / CINCO SETORES" 52 133 1.7 *destaque*)
  (loop for linha in (estado-setores-guerra guerra) for indice from 0
        do (desenhar-texto linha 70 (+ 173 (* indice 38)) 1.6 *gelo*))
  (loop for exercito in (guerra-exercitos guerra) for indice from 0
        do (desenhar-texto (format nil "~A / REFORÇOS ~D / ORDEM ~A"
                                   (exercito-nome exercito) (exercito-reforcos exercito)
                                   (exercito-ordem exercito))
                           650 (+ 173 (* indice 48)) 1.7 *gelo*))
  (when (guerra-invasao guerra)
    (retangulo 650 275 540 65 '(.35 .055 .04 .75))
    (desenhar-texto "INVASÃO / MONSTROS A CAMINHO DO RUÍDO" 670 297 1.5 *destaque*))
  (desenhar-texto "ORDENS: ATAQUE · DEFESA · REUNIÃO · RETIRADA" 52 420 1.5 *apagado*)
  (desenhar-texto "PING / TEXTO / MORTEIROS COM OBSERVADOR" 52 451 1.5 *apagado*)
  (loop for mensagem in (mensagens-recentes-guerra guerra 4) for indice from 0
        do (desenhar-texto (getf mensagem :texto) 650 (+ 380 (* indice 32)) 1.3 *apagado*))
  (desenhar-texto "ESC / PAUSAR    TAB / ESQUADRÃO    ENTER / CONFIRMAR" 52 665 1.4 *apagado*))
