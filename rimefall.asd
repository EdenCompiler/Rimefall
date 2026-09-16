(asdf:defsystem "rimefall/nucleo"
  :author "Bruno"
  :description "Simulação, tutorial e guerra distribuída de Rimefall."
  :serial t
  :depends-on ("usocket")
  :components ((:file "notas-de-campo") (:file "campo") (:file "guerra")
               (:file "invasoes") (:file "logistica") (:file "comunicacao")
               (:file "rede") (:file "persistencia") (:file "rimefall")))

(asdf:defsystem "rimefall"
  :author "Bruno"
  :description "Demo e guerra de sobrevivência ártica com a LWLGL."
  :version "0.3.0"
  :depends-on ("rimefall/nucleo" "lwlgl/opengl" "lwlgl/input" "lwlgl/openal")
  :serial t
  :components ((:file "apresentacao") (:file "interface") (:file "interface-guerra"))
  :in-order-to ((asdf:test-op (asdf:test-op "rimefall/testes"))))

(asdf:defsystem "rimefall/testes"
  :author "Bruno"
  :depends-on ("rimefall/nucleo")
  :components ((:file "testes"))
  :perform (asdf:test-op (operacao sistema)
             (declare (ignore operacao sistema))
             (uiop:symbol-call :rimefall :executar-testes)))
