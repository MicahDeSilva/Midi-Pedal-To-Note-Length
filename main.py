import mido

# Select midi file to import here
mid = mido.MidiFile('Arctic-Monkeys-Keys-Midi.mid')

new_mid = mido.MidiFile()
track = mido.MidiTrack()
mid.tracks.append(track)

notes_held = []

pedal_on = False
ghost_note_on = False

# Parse messages in passed file
for msg in mid.tracks[0]:
    write = True
    print(msg.time)
     
    # Check if pedal has been pressed
    if (msg.type == 'control_change'):
        write = False
        if(msg.value > 0 and not pedal_on):
            print("Pedal on")
            pedal_on = True
        elif(msg.value == 0 and pedal_on):
            print("Pedal off")
            pedal_on = False
            # Release all notes that were held
            while(len(notes_held) > 0):
                n = notes_held.pop()
                track.append(mido.Message('note_off', channel=n.channel, note=n.note, velocity=n.velocity, time=0))
        
        # We will not write this pedal message to our new file, so we must write a ghost note (silent note) to fill in the time that this message would have filled    
        if(ghost_note_on):
            track.append(mido.Message('note_off', channel=0, note=1, velocity=0, time=msg.time))
            ghost_note_on = False
        else:
            track.append(mido.Message('note_on', channel=0, note=1, velocity=0, time=msg.time))
            ghost_note_on = True
    
    # If the pedal is still held when a note_off signal is found, we must not write this note_off message to the new file,
    # Instead, we should record that the note is held so that the note_off message can be written when the pedal is raised.
    if(msg.type == 'note_off' and pedal_on):
        write = False
        notes_held.append(msg)
        # More ghost notes to keep timing consistent (as we are not writing this note)
        if(ghost_note_on):
            track.append(mido.Message('note_off', channel=0, note=1, velocity=0, time=msg.time))
            ghost_note_on = False
        else:
            track.append(mido.Message('note_on', channel=0, note=1, velocity=0, time=msg.time))
            ghost_note_on = True
        
    # If a note held by the pedal is played again, we must send a note_off signal first to reset the note   
    if(msg.type == 'note_on' and pedal_on):
        note_held = False
        array_index = -1
        i = 0
        
        for note in notes_held:
            if (msg.note == note.note):
                note_held = True
                array_index = i
                break
            i += 1
            
        if(note_held):
            n = notes_held[array_index]
            track.append(mido.Message('note_off', channel=n.channel, note=n.note, velocity=n.velocity, time=0))
            notes_held.remove(n)
    
    if(write == True):
        track.append(msg)

# Save as new file
mid.save('Arctic.mid')