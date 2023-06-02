import db from "../firebase";
import { collection, doc, getDoc } from "firebase/firestore";

export async function storageDataLoader() {
    const chartref = collection(db, "chart");
    const q = await getDoc(doc(chartref, "chart1"));
    return q.data();
}