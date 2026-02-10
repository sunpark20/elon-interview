class Interview < ApplicationRecord
  belongs_to :parent, class_name: "Interview", optional: true
  has_many :clips, class_name: "Interview", foreign_key: "parent_id", dependent: :nullify

  validates :youtube_id, presence: true, uniqueness: true
  validates :title, presence: true
  validates :youtube_url, presence: true

  scope :originals, -> { where(is_original: true) }
  scope :chronological, -> { order(interview_date: :desc) }
  scope :by_interviewer, ->(name) { where(interviewer: name) }
  scope :by_year, ->(year) { where(interview_date: Date.new(year)..Date.new(year, 12, 31)) }

  def clip?
    parent_id.present?
  end

  def formatted_duration
    return "" if duration.nil? || duration.zero?
    hours = duration / 3600
    minutes = (duration % 3600) / 60
    if hours > 0
      "#{hours}h #{minutes}m"
    else
      "#{minutes}m"
    end
  end

  def year
    interview_date&.year
  end
end
