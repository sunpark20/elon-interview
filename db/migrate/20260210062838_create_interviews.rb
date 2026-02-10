class CreateInterviews < ActiveRecord::Migration[8.1]
  def change
    create_table :interviews do |t|
      t.string :youtube_id, null: false
      t.string :title, null: false
      t.date :interview_date
      t.string :interviewer
      t.text :summary
      t.string :youtube_url, null: false
      t.string :thumbnail_url
      t.integer :duration, default: 0
      t.text :transcript
      t.boolean :is_original, default: true
      t.references :parent, foreign_key: { to_table: :interviews }, null: true
      t.string :channel_name
      t.string :channel_id

      t.timestamps
    end
    add_index :interviews, :youtube_id, unique: true
    add_index :interviews, :interview_date
    add_index :interviews, :is_original
  end
end
