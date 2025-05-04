from keybert import KeyLLM


def keyword_generation(documents, llm):
    # candidate_keywords = [
    #     ["nền tảng xem phim trực tuyến", "bộ phim", "chương trình truyền hình", "tìm kiếm", "xem", "phim mới nhất"]]
    # keywords = kw_model.extract_keywords(description, candidate_keywords=candidate_keywords)

    kw_model = KeyLLM(llm)
    keywords = kw_model.extract_keywords(documents)

    return keywords


"""
inside response of models, there should be these data
{
  "id": "aa0b828e-f9cf-484d-a84d-cb62f556e841",
  "summary": "Ice cream is a frozen dessert made by whipping a cream base and liquid nitrogen together. It is then flavoured with sweeteners, spices and fruits. Ice cream can also be made using alternative milks, such as soy or almond, for those who are lactose intolerant or vegan.",
  "meta": {
    "api_version": {
      "version": "1"
    },
    "billed_units": {
      "input_tokens": 321,
      "output_tokens": 55
  },
  "tokens": {
    "input_tokens": 7596,
    "output_tokens": 645
    }
  }
}
"""
