(in-package #:rimefall)

(defparameter *ordens-guerra* '(:atacar :defender :reunir :retirar))
(defparameter *canais-guerra* '(:esquadrao :comando))

(defun enviar-ordem-guerra (guerra jogador ordem)
  (when (member ordem *ordens-guerra*)
    (let ((resultado (ordem-esquadrao-guerra jogador ordem)))
      (when resultado
        (emitir-mensagem-guerra guerra (jogador-guerra-exercito jogador)
                                (format nil "Ordem do esquadrão: ~A." ordem) :comando))
      resultado)))

(defun enviar-ping-guerra (guerra jogador x z rotulo)
  (when (adicionar-marcador-guerra guerra jogador x z rotulo)
    (emitir-mensagem-guerra guerra (jogador-guerra-exercito jogador)
                            (format nil "Marcador: ~A." rotulo) :comando)
    t))

(defun enviar-texto-guerra (guerra jogador texto &optional (canal :esquadrao))
  (when (member canal *canais-guerra*)
    (emitir-mensagem-guerra guerra (jogador-guerra-exercito jogador)
                            (subseq (princ-to-string texto) 0
                                    (min 240 (length (princ-to-string texto)))) canal)))

(defun mensagens-recentes-guerra (guerra &optional (quantidade 8))
  (subseq (guerra-mensagens guerra) 0
          (min quantidade (length (guerra-mensagens guerra)))))
