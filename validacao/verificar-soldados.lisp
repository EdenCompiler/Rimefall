;;; Capturas controladas dos modelos reais no renderizador LWLGL.
;;; Executar somente em X11 virtual, com WAYLAND_DISPLAY removido.
(require :asdf)
(load (merge-pathnames "quicklisp/setup.lisp" (user-homedir-pathname)))
(asdf:load-asd (merge-pathnames "../rimefall.asd" *load-truename*))
(asdf:load-system "rimefall")
(in-package #:rimefall)

(defun verificar-apresentacao-soldados ()
  (assert (and (uiop:getenv "DISPLAY") (not (uiop:getenv "WAYLAND_DISPLAY"))))
  (let* ((pasta (merge-pathnames (format nil "rimefall-soldados-~D/" (get-universal-time))
                                (uiop:temporary-directory)))
         (*pasta-dados* (merge-pathnames "dados/" pasta))
         (*pasta-configuracao* (merge-pathnames "preferencias/" pasta))
         (nomes '(processar-interface atualizar-guerra atualizar-logistica-guerra
                  atualizar-invasao-guerra atualizar-campo))
         (originais (mapcar #'symbol-function nomes)))
    (unwind-protect
         (progn
           ;; As capturas inspecionam pose e escala; o combate fica congelado
           ;; apenas neste processo de teste, sem alterar as regras do jogo.
           (dolist (nome (rest nomes))
             (setf (symbol-function nome) (lambda (&rest argumentos) (declare (ignore argumentos)))))
           (dolist (etapa '(:guerra :distante :demo :recarga))
             (let ((preparado nil) (capturas (merge-pathnames (format nil "~A/" etapa) pasta)))
               (ensure-directories-exist capturas)
               (setf (symbol-function 'processar-interface)
                     (lambda (sessao estado janela)
                       (declare (ignore estado janela))
                       (unless preparado
                         (if (member etapa '(:guerra :distante))
                             (let* ((guerra *guerra-atual*) (local (jogador-local-guerra guerra)))
                               (setf *hud-guerra-visivel* nil
                                     (jogador-guerra-x local) -6.0 (jogador-guerra-z local) -55.0
                                     (jogador-guerra-angulo local) 0.0
                                     (jogador-guerra-inclinacao local) -.04)
                               (loop for jogador in (remove local (guerra-jogadores guerra)) for indice from 0
                                     do (setf (jogador-guerra-estado jogador) (if (< indice 5) :ativo :morto)
                                              (jogador-guerra-x jogador) (+ -6.0 (* 1.3 (- indice 2)))
                                              (jogador-guerra-z jogador) -61.0
                                              (jogador-guerra-angulo jogador) (float pi 1.0)
                                              (jogador-guerra-movimento jogador) .5
                                              (jogador-guerra-passada jogador) .55)))
                             (let ((nova (nova-sessao)))
                               (confirmar-notas nova)
                               (setf (soldado-x (sessao-soldado nova)) 0.0
                                     (soldado-z (sessao-soldado nova)) 18.5)
                               (encerrar-vida nova) (abrir-notas nova) (confirmar-notas nova)
                               (setf (soldado-x (sessao-soldado nova)) 0.0
                                     (soldado-z (sessao-soldado nova)) 22.0
                                     (soldado-angulo (sessao-soldado nova)) 0.0
                                     (soldado-inclinacao (sessao-soldado nova)) -.40
                                     (sessao-inimigos nova) nil (sessao-tempo nova) 20.0)
                               (when (eq etapa :recarga)
                                 (decf (soldado-carregador (sessao-soldado nova)))
                                 (iniciar-recarga nova)
                                 (setf (soldado-recarga (sessao-soldado nova))
                                       (* .5 (duracao-recarga (soldado-arma (sessao-soldado nova))))))
                               (setf sessao nova)))
                         (setf preparado t))
                       sessao))
               ;; A segunda cena verifica a malha inteira sob a mesma câmera,
               ;; para comparar escala e origem com a versão articulada.
               (let ((desenhar-original (symbol-function 'desenhar-soldado-articulado)))
                 (unwind-protect
                      (progn
                        (when (eq etapa :distante)
                          (setf (symbol-function 'desenhar-soldado-articulado)
                                (lambda (guerra jogador base uniforme &optional articulado)
                                  (declare (ignore articulado))
                                  (funcall desenhar-original guerra jogador base uniforme nil))))
                        (iniciar-jogo :guerra (member etapa '(:guerra :distante)) :sem-audio t
                                      :quadros-maximos 35 :sincronizar nil :pasta-capturas capturas))
                   (setf (symbol-function 'desenhar-soldado-articulado) desenhar-original)))
               (uiop:run-program
                (list "convert" (namestring (merge-pathnames "quadro-025.ppm" capturas))
                      (namestring (asdf:system-relative-pathname "rimefall"
                                  (format nil "validacao/soldados-~(~A~).png" etapa)))))
               (format t "~&Captura de soldados concluída: ~A.~%" etapa))))
      (loop for nome in nomes for original in originais do (setf (symbol-function nome) original)))))

(verificar-apresentacao-soldados)
