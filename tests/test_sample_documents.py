from src.config import SAMPLE_DOCUMENTS_DIR


def test_sample_documents_exist_and_are_original():
    required = {
        "Employee_Handbook.pdf",
        "Leave_Policy.pdf",
        "Travel_Policy.pdf",
        "IT_Security_Policy.pdf",
        "Remote_Work_Policy.docx",
        "Office_Locations.txt",
    }
    names = {p.name for p in SAMPLE_DOCUMENTS_DIR.iterdir() if p.is_file()}
    missing = required - names
    assert not missing, f"Missing sample files: {missing}"
    txt = (SAMPLE_DOCUMENTS_DIR / "Office_Locations.txt").read_text(encoding="utf-8")
    assert "Northline" in txt
    assert "Manchester Studio" in txt
