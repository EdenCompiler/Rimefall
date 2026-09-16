(in-package #:rimefall)

;;; Protótipo de guerra: a simulação é independente da janela e do tutorial.
(defparameter *duracao-guerra* (* 60 60.0))
(defparameter *tempo-incapacitado* 45.0)
(defparameter *tempo-reforco* 10.0)
(defparameter *quantidade-reforcos-prototipo* 32)
(defparameter *funcoes-guerra* '(:fuzileiro :medico :suporte :engenheiro :comandante))

(defstruct (quartel-general (:constructor criar-quartel-general)
                            (:predicate quartel-general-p))
  id nome x z (vida 1000.0) (vida-maxima 1000.0))
(defstruct (exercito (:constructor criar-exercito)
                     (:predicate exercito-p))
  id nome cor quartel-general (reforcos *quantidade-reforcos-prototipo*)
  (fila-reforcos nil) (ordem :defender) (mensagens nil))
(defstruct (setor-guerra (:constructor criar-setor-guerra)
                         (:predicate setor-guerra-p))
  id nome x z raio (ordem 0) dono (progresso 0.0) (contestacao 0.0))
(defstruct (esquadrao-guerra (:constructor criar-esquadrao-guerra)
                             (:predicate esquadrao-guerra-p))
  id exercito nome (lider nil) jogadores (ordem :reunir) marcador)
(defstruct (jogador-guerra (:constructor criar-jogador-guerra)
                           (:predicate jogador-guerra-p))
  id nome exercito esquadrao funcao (bot-p t) (estado :ativo)
  (x 0.0) (z 0.0) (angulo 0.0) (incapacitado-em 0.0)
  (estabilizado-p nil) (reanimacoes 0) (eliminacoes 0)
  (arma :fuzil) (municao 30) (ultima-ordem nil) (ultima-mensagem ""))
(defstruct (comando-guerra (:constructor criar-comando-guerra)
                          (:predicate comando-guerra-p))
  quadro jogador tipo dados)
(defstruct (veiculo-guerra (:constructor criar-veiculo-guerra)
                          (:predicate veiculo-guerra-p))
  id exercito tipo x z (vida 500.0) (capacidade 8) passageiros (carga 0)
  motorista (velocidade 12.0) (destino-x 0.0) (destino-z 0.0))
(defstruct (morteiro-guerra (:constructor criar-morteiro-guerra)
                           (:predicate morteiro-guerra-p))
  id exercito x z operador observador (municao 12) (recarga 0.0)
  (alvo-x 0.0) (alvo-z 0.0) (dispersao 12.0))
(defstruct (guerra (:constructor criar-guerra)
                   (:predicate guerra-p))
  (fase :preparacao) (tempo 0.0) (quadro 0) duracao
  exercitos setores esquadroes jogadores veiculos morteiros
  (mensagens nil) (marcadores nil) (sons nil) (pressao-sonora 0.0)
  (invasao nil) (semente 9173) (historico nil) (fila-comandos nil)
  (modo :offline) vencedor (divergencias nil))
(defvar *guerra-atual* nil)

(defparameter *nomes-exercitos*
  '((:aurora "União Aurora" :azul)
    (:bruma "Liga da Bruma" :cinza)))
(defparameter *nomes-setores-guerra*
  '("Passagem do Rio" "Aldeia de Gelo" "Linha das Trincheiras"
    "Pátio Industrial" "Colina do Farol"))

(defun criar-setores-guerra ()
  (loop for nome in *nomes-setores-guerra*
        for indice from 0
        collect (criar-setor-guerra :id indice :nome nome :x 0.0
                                     :z (- (* indice 120.0) 240.0)
                                     :raio 82.0 :ordem indice)))

(defun criar-exercitos-guerra ()
  (loop for (id nome cor) in *nomes-exercitos*
        for z in '(-500.0 500.0)
        collect (criar-exercito :id id :nome nome :cor cor
                                :quartel-general
                                (criar-quartel-general :id id :nome (format nil "QG ~A" nome)
                                                       :x 0.0 :z z))))

(defun localizar-exercito-guerra (guerra id)
  (find id (guerra-exercitos guerra) :key #'exercito-id))

(defun localizar-jogador-guerra (guerra id)
  (find id (guerra-jogadores guerra) :key #'jogador-guerra-id))

(defun criar-guerra-offline (&key (jogadores-por-lado 8))
  "Cria uma batalha pequena, determinística, pronta para bots ou clientes."
  (let* ((exercitos (criar-exercitos-guerra))
         (guerra (criar-guerra :duracao *duracao-guerra* :exercitos exercitos
                               :setores (criar-setores-guerra))))
    (loop for exercito in exercitos
          for lado from 0
          do (loop for numero below jogadores-por-lado
                   for esquadrao-id = (floor numero 4)
                   for funcao = (nth (mod numero (length *funcoes-guerra*)) *funcoes-guerra*)
                   for id = (+ (* lado 100) numero)
                   for esquadrao = (or (find (+ (* lado 10) esquadrao-id) (guerra-esquadroes guerra)
                                              :key #'esquadrao-guerra-id)
                                       (let ((novo (criar-esquadrao-guerra
                                                    :id (+ (* lado 10) esquadrao-id)
                                                    :exercito exercito
                                                    :nome (format nil "Esquadrão ~D" (1+ esquadrao-id)))))
                                         (push novo (guerra-esquadroes guerra))
                                         novo))
                   for jogador = (criar-jogador-guerra
                                  :id id :nome (format nil "~A ~D" (exercito-nome exercito) (1+ numero))
                                  :exercito exercito :esquadrao esquadrao :funcao funcao
                                  :x 0.0 :z (if (zerop lado) -470.0 470.0))
                   do (push jogador (guerra-jogadores guerra))
                      (push jogador (esquadrao-guerra-jogadores esquadrao))
                      (when (eq funcao :comandante) (setf (esquadrao-guerra-lider esquadrao) jogador))))
    (setf (guerra-esquadroes guerra) (nreverse (guerra-esquadroes guerra))
          (guerra-jogadores guerra) (nreverse (guerra-jogadores guerra))
          (guerra-fase guerra) :combate)
    guerra))

(defun guerra-ativa-p (guerra) (eq (guerra-fase guerra) :combate))
(defun jogador-ativo-p (jogador) (eq (jogador-guerra-estado jogador) :ativo))
(defun distancia-guerra (a b)
  (sqrt (+ (expt (- (jogador-guerra-x a) (jogador-guerra-x b)) 2)
           (expt (- (jogador-guerra-z a) (jogador-guerra-z b)) 2))))

(defun emitir-mensagem-guerra (guerra exercito texto &optional (canal :esquadrao))
  (push (list :tempo (guerra-tempo guerra) :exercito (exercito-id exercito)
              :canal canal :texto texto) (guerra-mensagens guerra))
  (push (list :tempo (guerra-tempo guerra) :canal canal :texto texto)
        (exercito-mensagens exercito))
  texto)

(defun adicionar-marcador-guerra (guerra jogador x z rotulo)
  (when (and (jogador-ativo-p jogador) (member (jogador-guerra-funcao jogador)
                                               '(:comandante :engenheiro)))
    (push (list :jogador (jogador-guerra-id jogador) :x (float x) :z (float z)
                :rotulo (subseq (princ-to-string rotulo) 0
                                (min 48 (length (princ-to-string rotulo)))))
          (guerra-marcadores guerra))
    t))

(defun ordem-esquadrao-guerra (jogador ordem)
  (let ((esquadrao (jogador-guerra-esquadrao jogador)))
    (when (or (eq jogador (esquadrao-guerra-lider esquadrao))
              (eq (jogador-guerra-funcao jogador) :comandante))
      (setf (esquadrao-guerra-ordem esquadrao) ordem)
      (dolist (membro (esquadrao-guerra-jogadores esquadrao))
        (setf (jogador-guerra-ultima-ordem membro) ordem))
      ordem)))

(defun incapacitar-jogador-guerra (guerra jogador)
  (when (jogador-ativo-p jogador)
    (setf (jogador-guerra-estado jogador) :incapacitado
          (jogador-guerra-incapacitado-em jogador) (guerra-tempo guerra)
          (jogador-guerra-estabilizado-p jogador) nil)
    (emitir-mensagem-guerra guerra (jogador-guerra-exercito jogador)
                            (format nil "~A está incapacitado." (jogador-guerra-nome jogador))
                            :esquadrao)
    t))

(defun estabilizar-jogador-guerra (guerra medico alvo)
  (when (and (eq (jogador-guerra-funcao medico) :medico)
             (jogador-ativo-p medico)
             (eq (jogador-guerra-estado alvo) :incapacitado)
             (eq (jogador-guerra-exercito medico) (jogador-guerra-exercito alvo))
             (< (distancia-guerra medico alvo) 4.0))
    (setf (jogador-guerra-estabilizado-p alvo) t)
    (emitir-mensagem-guerra guerra (jogador-guerra-exercito medico)
                            "Ferido estabilizado. Reanimação possível." :esquadrao)
    t))

(defun reanimar-jogador-guerra (guerra medico alvo)
  (when (and (eq (jogador-guerra-funcao medico) :medico)
             (jogador-ativo-p medico)
             (jogador-guerra-estabilizado-p alvo)
             (< (distancia-guerra medico alvo) 4.0))
    (setf (jogador-guerra-estado alvo) :ativo
          (jogador-guerra-estabilizado-p alvo) nil)
    (incf (jogador-guerra-reanimacoes alvo))
    t))

(defun matar-jogador-guerra (guerra jogador &optional (causa "Baixa em combate"))
  (when (member (jogador-guerra-estado jogador) '(:ativo :incapacitado))
    (let ((exercito (jogador-guerra-exercito jogador)))
      (setf (jogador-guerra-estado jogador) :morto)
      (decf (exercito-reforcos exercito))
      (push (list :jogador (jogador-guerra-id jogador) :causa causa
                  :tempo (guerra-tempo guerra)) (guerra-historico guerra))
      (when (plusp (exercito-reforcos exercito))
        (push jogador (exercito-fila-reforcos exercito)))
      (when (not (plusp (exercito-reforcos exercito)))
        (setf (guerra-fase guerra) :derrota
              (guerra-vencedor guerra)
              (exercito-id (find-if (lambda (outro) (not (eq outro exercito)))
                                    (guerra-exercitos guerra)))))
      t)))

(defun aplicar-dano-qg (guerra exercito dano origem)
  (let ((qg (exercito-quartel-general exercito)))
    (decf (quartel-general-vida qg) dano)
    (emitir-mensagem-guerra guerra exercito
                            (format nil "~A sofreu ~,0F de dano no QG." origem dano) :comando)
    (when (<= (quartel-general-vida qg) 0)
      (let ((adversario (find-if (lambda (outro) (not (eq outro exercito)))
                                 (guerra-exercitos guerra))))
        (setf (guerra-fase guerra) :vitoria
              (guerra-vencedor guerra) (and adversario (exercito-id adversario))))
      :destruido)))

(defun solicitar-reforco-guerra (guerra jogador)
  (when (and (eq (jogador-guerra-estado jogador) :morto)
             (plusp (exercito-reforcos (jogador-guerra-exercito jogador))))
    (pushnew jogador (exercito-fila-reforcos (jogador-guerra-exercito jogador)))
    t))

(defun atualizar-reforcos-guerra (guerra intervalo)
  (declare (ignore intervalo))
  (when (>= (guerra-tempo guerra) *tempo-reforco*)
    (dolist (exercito (guerra-exercitos guerra))
      (let ((jogador (pop (exercito-fila-reforcos exercito))))
        (when jogador
          (setf (jogador-guerra-estado jogador) :ativo
                (jogador-guerra-z jogador) (quartel-general-z (exercito-quartel-general exercito))
                (jogador-guerra-x jogador) 0.0)
          (emitir-mensagem-guerra guerra exercito
                                  (format nil "~A retornou pelo ponto de reunião." (jogador-guerra-nome jogador))
                                  :comando))))))

(defun jogadores-no-setor (guerra setor exercito)
  (count-if (lambda (jogador)
              (and (eq (jogador-guerra-exercito jogador) exercito)
                   (jogador-ativo-p jogador)
                   (<= (sqrt (+ (expt (- (jogador-guerra-x jogador) (setor-guerra-x setor)) 2)
                                (expt (- (jogador-guerra-z jogador) (setor-guerra-z setor)) 2)))
                       (setor-guerra-raio setor))))
            (guerra-jogadores guerra)))

(defun setor-liberado-p (guerra setor)
  (let ((indice (setor-guerra-ordem setor)))
    (or (zerop indice)
        (eq (setor-guerra-dono (nth (1- indice) (guerra-setores guerra)))
            :aurora)
        (eq (setor-guerra-dono (nth (1- indice) (guerra-setores guerra))) :bruma))))

(defun atualizar-setores-guerra (guerra intervalo)
  (dolist (setor (guerra-setores guerra))
    (when (setor-liberado-p guerra setor)
      (let* ((aurora (localizar-exercito-guerra guerra :aurora))
             (bruma (localizar-exercito-guerra guerra :bruma))
             (contagem-a (jogadores-no-setor guerra setor aurora))
             (contagem-b (jogadores-no-setor guerra setor bruma))
             (diferenca (- contagem-a contagem-b)))
        (setf (setor-guerra-contestacao setor) (float diferenca))
        (cond ((plusp diferenca)
               (incf (setor-guerra-progresso setor) (* intervalo .025 diferenca)))
              ((minusp diferenca)
               (decf (setor-guerra-progresso setor) (* intervalo .025 (abs diferenca))))
              (t nil))
        (setf (setor-guerra-progresso setor) (max -1.0 (min 1.0 (setor-guerra-progresso setor))))
        (when (>= (setor-guerra-progresso setor) 1.0)
          (setf (setor-guerra-dono setor) :aurora (setor-guerra-progresso setor) 0.0)
          (emitir-mensagem-guerra guerra aurora
                                  (format nil "Setor capturado: ~A." (setor-guerra-nome setor)) :comando))
        (when (<= (setor-guerra-progresso setor) -1.0)
          (setf (setor-guerra-dono setor) :bruma (setor-guerra-progresso setor) 0.0)
          (emitir-mensagem-guerra guerra bruma
                                  (format nil "Setor capturado: ~A." (setor-guerra-nome setor)) :comando))))))

(defun atualizar-bots-guerra (guerra intervalo)
  (dolist (jogador (guerra-jogadores guerra))
    (when (and (jogador-guerra-bot-p jogador) (jogador-ativo-p jogador))
      (let* ((exercito (jogador-guerra-exercito jogador))
             (alvo (find-if (lambda (setor)
                              (not (eq (setor-guerra-dono setor) (exercito-id exercito))))
                            (guerra-setores guerra)))
             (z (if alvo (setor-guerra-z alvo) (quartel-general-z (exercito-quartel-general exercito))))
             (direcao (if (< (jogador-guerra-z jogador) z) 1.0 -1.0)))
        (incf (jogador-guerra-z jogador) (* direcao intervalo 4.0))
        (setf (jogador-guerra-angulo jogador) (if (plusp direcao) 0.0 pi))))))

(defun aplicar-comando-guerra (guerra comando)
  "Valida permissões e aplica um comando já ordenado pelo quadro."
  (let* ((jogador (localizar-jogador-guerra guerra (comando-guerra-jogador comando)))
         (tipo (comando-guerra-tipo comando)) (dados (comando-guerra-dados comando)))
    (when (and jogador (or (<= (comando-guerra-quadro comando) (1+ (guerra-quadro guerra)))
                           (= (comando-guerra-quadro comando) (1+ (guerra-quadro guerra)))))
      (case tipo
        (:mover (when (jogador-ativo-p jogador)
                  (incf (jogador-guerra-x jogador) (float (getf dados :x)))
                  (incf (jogador-guerra-z jogador) (float (getf dados :z))) t))
        (:ordem (ordem-esquadrao-guerra jogador (getf dados :ordem)))
        (:marcador (adicionar-marcador-guerra guerra jogador (getf dados :x) (getf dados :z) (getf dados :rotulo)))
        (:texto (let ((texto (subseq (princ-to-string (getf dados :texto)) 0
                                     (min 240 (length (princ-to-string (getf dados :texto)))))))
                  (setf (jogador-guerra-ultima-mensagem jogador) texto)
                  (emitir-mensagem-guerra guerra (jogador-guerra-exercito jogador) texto (getf dados :canal))))
        (:incapacitar (incapacitar-jogador-guerra guerra jogador))
        (:estabilizar (estabilizar-jogador-guerra guerra jogador
                         (localizar-jogador-guerra guerra (getf dados :alvo))))
        (:reanimar (reanimar-jogador-guerra guerra jogador
                     (localizar-jogador-guerra guerra (getf dados :alvo))))
        (:reforco (solicitar-reforco-guerra guerra jogador))
        (otherwise nil)))))

(defun hash-estado-guerra (guerra)
  "Hash estável dos campos de simulação para conferência entre clientes."
  (sxhash (list (guerra-quadro guerra) (guerra-fase guerra)
                (mapcar (lambda (setor) (list (setor-guerra-id setor) (setor-guerra-dono setor)
                                               (setor-guerra-progresso setor))) (guerra-setores guerra))
                (mapcar (lambda (jogador) (list (jogador-guerra-id jogador)
                                                (jogador-guerra-estado jogador)
                                                (round (jogador-guerra-x jogador))
                                                (round (jogador-guerra-z jogador))))
                        (guerra-jogadores guerra)))))

(defun atualizar-guerra (guerra intervalo)
  (when (guerra-ativa-p guerra)
    (incf (guerra-tempo guerra) intervalo)
    (incf (guerra-quadro guerra))
    (dolist (comando (sort (copy-list (guerra-fila-comandos guerra)) #'<
                           :key #'comando-guerra-quadro))
      (aplicar-comando-guerra guerra comando))
    (setf (guerra-fila-comandos guerra) nil)
    (atualizar-bots-guerra guerra intervalo)
    (atualizar-setores-guerra guerra intervalo)
    (atualizar-reforcos-guerra guerra intervalo)
    (dolist (jogador (guerra-jogadores guerra))
      (when (and (eq (jogador-guerra-estado jogador) :incapacitado)
                 (> (- (guerra-tempo guerra) (jogador-guerra-incapacitado-em jogador))
                    *tempo-incapacitado*)
                 (not (jogador-guerra-estabilizado-p jogador)))
        (matar-jogador-guerra guerra jogador "Sangramento")))
    (when (>= (guerra-tempo guerra) (guerra-duracao guerra))
      (setf (guerra-fase guerra) :empate)))
  guerra)
