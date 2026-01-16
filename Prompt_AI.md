CASE 1:
GPT
như đã nói giờ với case 1 là video youtube có transcript để fetch thì đã dễ dàng lấy được text rồi
tuy nhiên tao lại có các trường hợp như là:
phần auto generate transcript có thể có các từ bị sai cú pháp, ngữ pháp thì có phải xử lí không
phần video quá dài(tầm 2-3 tiếng) thì lượng context khá lớn tao mới fetch thử 1 cái postcard tầm 1 tiếng đã tầm 8-9000 token rồi thì nếu không chia chunks mà ném thẳng vào prompt cho gemini thì có bị khó quá không
với cả với các video mang tính bài giảng hay cũng có thể là postcard đó tất nhiên là trong video đó có nhiều chủ đề và vấn đề là tao cần chia các phần đấy theo từng đề mục kèm theo timestamp+summary cho các đề mục đó, phần này thì chắc chắn phải làm vì bài toán yêu cầu như vậy. Chốt lại là tao định làm một node LLM nhẹ chỉ để chia video nếu dài thành các đề mục có thể coi luôn là các chunks, và khi đi vào logic chính là dùng gemini để summary thì tao định thêm 1 cái term memory cho mỗi video tức là sẽ đưa từng chunk một để summary sau mỗi chunk thì sẽ cập nhật cái tern memory đó và đưa nó vào prompt luôn để giữ context tổng thể của video tất nhiên đánh đổi là thời gian phản hồi và chi phí + số request lớn hơn rồi nhưng tao nghĩ là cũng đáng làm và đáng thử đấy
trên đây là các suy nghĩ và phân tích của tao về case 1 : video có thể fetch được transcript
-> không cần sửa lỗi cú pháp + ngữ pháp cho gemini đã xử lí được rất tốt
-> nên dùng 1 node LLM nhẹ để chia chunks theo semantic
Transcript
   ↓
Light LLM (Topic Segmenter)
   ↓
[
  {topic, start, end, text},
  {topic, start, end, text},
  ...
]
   ↓
Heavy LLM (Gemini Summary)
