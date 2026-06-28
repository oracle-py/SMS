import "./Modal.css";
import Button from "./Button";

function Modal({

    open,

    title,

    children,

    onClose,

    onConfirm,

    confirmText = "Save",

    cancelText = "Cancel",

    loading = false

}){

    if(!open) return null;

    return(

        <div className="modal-overlay">

            <div className="modal">

                <div className="modal-header">

                    <h2>{title}</h2>

                    <button

                        className="modal-close"

                        onClick={onClose}

                    >

                        ×

                    </button>

                </div>

                <div className="modal-body">

                    {children}

                </div>

                <div className="modal-footer">

                    <Button

                        variant="secondary"

                        onClick={onClose}

                    >

                        {cancelText}

                    </Button>

                    <Button

                        loading={loading}

                        onClick={onConfirm}

                    >

                        {confirmText}

                    </Button>

                </div>

            </div>

        </div>

    );

}

export default Modal;