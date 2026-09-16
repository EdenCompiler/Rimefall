(in-package #:rimefall)

;;; A rede não simula o mundo. Ela ordena comandos e compara hashes dos clientes.
(defstruct (cliente-rede-guerra (:constructor criar-cliente-rede-guerra))
  id fluxo endereco ultimo-quadro (hash nil) (conectado-p t))
(defstruct (rele-guerra (:constructor criar-rele-guerra)
                       (:predicate rele-guerra-p))
  (quadro 0) (clientes nil) (comandos nil) (hashes nil) (divergencias nil)
  (porta 27873) (ativo-p nil) socket)

(defun codificar-comando-rede (comando)
  (list :comando (comando-guerra-quadro comando) (comando-guerra-jogador comando)
        (comando-guerra-tipo comando) (comando-guerra-dados comando)))

(defun dados-rede-p (valor)
  (or (null valor) (keywordp valor) (numberp valor) (stringp valor)
      (and (consp valor) (every #'dados-rede-p valor))))

(defun decodificar-comando-rede (valor)
  (when (and (consp valor) (= (length valor) 5) (eq (first valor) :comando)
             (integerp (second valor)) (integerp (third valor))
             (keywordp (fourth valor)) (dados-rede-p (fifth valor)))
    (criar-comando-guerra :quadro (second valor) :jogador (third valor)
                          :tipo (fourth valor) :dados (fifth valor))))

(defun enfileirar-comando-rede (rele comando)
  (when (and (rele-guerra-ativo-p rele) (comando-guerra-p comando)
             (<= (rele-guerra-quadro rele) (comando-guerra-quadro comando)
                 (+ 2 (rele-guerra-quadro rele))))
    (push comando (rele-guerra-comandos rele))
    t))

(defun registrar-hash-rede (rele cliente quadro hash)
  (when (and (rele-guerra-ativo-p rele) (cliente-rede-guerra-p cliente)
             (= quadro (rele-guerra-quadro rele)))
    (setf (cliente-rede-guerra-ultimo-quadro cliente) quadro
          (cliente-rede-guerra-hash cliente) hash)
    (let ((outros (remove cliente (rele-guerra-clientes rele))))
      (when (and outros (every (lambda (outro) (eql hash (cliente-rede-guerra-hash outro))) outros))
        t))))

(defun detectar-divergencia-rede (rele)
  (let ((hashes (remove nil (mapcar #'cliente-rede-guerra-hash (rele-guerra-clientes rele)))))
    (when (and hashes (not (apply #'= hashes)))
      (push (list :quadro (rele-guerra-quadro rele) :hashes hashes)
            (rele-guerra-divergencias rele))
      t)))

(defun criar-rele-local (&key (porta 27873))
  (criar-rele-guerra :porta porta :ativo-p t))

(defun avancar-rele-guerra (rele guerra)
  (when (rele-guerra-ativo-p rele)
    (incf (rele-guerra-quadro rele))
    (dolist (comando (sort (copy-list (rele-guerra-comandos rele)) #'<
                           :key #'comando-guerra-quadro))
      (push comando (guerra-fila-comandos guerra)))
    (setf (rele-guerra-comandos rele) nil)
    (atualizar-guerra guerra *passo-fixo*)
    (detectar-divergencia-rede rele)
    (hash-estado-guerra guerra)))

(defun preparar-cliente-rede (rele id)
  (let ((cliente (criar-cliente-rede-guerra :id id :ultimo-quadro (rele-guerra-quadro rele))))
    (push cliente (rele-guerra-clientes rele))
    cliente))

(defun remover-cliente-rede (rele cliente)
  (setf (cliente-rede-guerra-conectado-p cliente) nil
        (rele-guerra-clientes rele) (remove cliente (rele-guerra-clientes rele)))
  t)

(defun abrir-relé-rede (&key (endereco "0.0.0.0") (porta 27873))
  "Abre o relé TCP para conexão direta; a simulação continua fora do socket."
  (let ((rele (criar-rele-local :porta porta)))
    (setf (rele-guerra-socket rele)
          (usocket:socket-listen endereco porta :reuse-address t :element-type 'character
                                 :backlog 16))
    rele))

(defun aceitar-cliente-rede (rele)
  (when (and (rele-guerra-ativo-p rele) (rele-guerra-socket rele))
    (multiple-value-bind (socket endereco porta)
        (usocket:socket-accept (rele-guerra-socket rele))
      (let ((cliente (preparar-cliente-rede rele (length (rele-guerra-clientes rele)))))
        (setf (cliente-rede-guerra-fluxo cliente) (usocket:socket-stream socket)
              (cliente-rede-guerra-endereco cliente) (list endereco porta))
        cliente))))

(defun fechar-rele-rede (rele)
  (when (rele-guerra-socket rele) (usocket:socket-close (rele-guerra-socket rele)))
  (setf (rele-guerra-ativo-p rele) nil (rele-guerra-socket rele) nil)
  t)
