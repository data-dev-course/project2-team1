import db from "../firebase";
import { 
    doc, 
    getDoc, 
    getDocs,
    collection, 
    query, 
    orderBy, 
    limit, 
    startAfter,
    getCountFromServer
} from "firebase/firestore";

export const getTotalDoc = async (kindType='개') => {
    const collref = collection(db, "strayanimal", "차트12_유기동물_상세정보", `차트12_유기동물_상세정보_${kindType}`);
    const snapshot = await getCountFromServer(collref);
    return snapshot.data().count;
}

export const fetchPostData = async (pageParam=0, kindType='개', lastSnap, last=true) => {
    const collref = collection(db, "strayanimal", "차트12_유기동물_상세정보", `차트12_유기동물_상세정보_${kindType}`);
    let q;
    
    if (pageParam === 0) {
        q = query(collref, orderBy("happenDt", "desc"), limit(10));
    } else if (lastSnap===-1 && last) {
        const totalelem = await getTotalDoc();
        q = query(collref, orderBy("happenDt", "asc"), limit(totalelem%10));
    } else if (last) {
        const docsnap = await getDoc(doc(collref, lastSnap))
        q = query(collref, orderBy("happenDt", "desc"), startAfter(docsnap), limit(10));
    } else {
        const docsnap = await getDoc(doc(collref, lastSnap))
        q = query(collref, orderBy("happenDt", "asc"), startAfter(docsnap), limit(10));
    }
    const docsSnap = await getDocs(q)
    const docList = docsSnap.docs.map((doc) => {
        const data = doc.data();
        return {
            id: doc.id,
            ...data,
        };
    })
    console.log({firstId: docList[0].id, lastId: docList[docList.length-1].id, pages:docList})
    return {firstId: docList[0].id, lastId: docList[docList.length-1].id, pages:docList};
}